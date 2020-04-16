import datetime
import json
import logging
import time
import threading
from models import MonitoringFailed
from sqlalchemy.orm import sessionmaker
from prometheus_http_client import Prometheus

logger = logging.getLogger('node_monitoring_worker')


# process_node_monitoring receives node monitoring data from Prometheus
# and inserts it to db. This work happens in a separate thread.
def process_node_monitoring(db_engine):
    session_factory = sessionmaker(bind=db_engine)

    db_session = None
    logger.info("node monitoring started")
    while True:
        try:
            prometheus = Prometheus()
            db_session = session_factory()

            data = json.loads(prometheus.query(metric='ALERTS{alertname="provider_down", alertstate="firing"}'))
            db_session.query(MonitoringFailed).delete()
            for r in data["data"]["result"]:
                db_session.add(MonitoringFailed(r["metric"]["provider"], r["metric"]["service_type"]))

            db_session.commit()
            logger.info("Committed node monitoring batch")
        except Exception:
            logger.error("Failed to process node monitoring status:", exc_info=True)
            if db_session is not None:
                db_session.rollback()
        finally:
            if db_session is not None:
                db_session.close()

        time.sleep(60)


def start_node_monitoring_worker(db_engine):
    x = threading.Thread(target=process_node_monitoring, args=(db_engine,), daemon=True)
    x.start()
