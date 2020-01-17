import datetime
import json
import logging
import time
import threading
from models import PaymentTokens
from sqlalchemy.orm import sessionmaker
from prometheus_http_client import Prometheus

logger = logging.getLogger('node_payments_worker')


# process_node_payments receives node payments data from Prometheus
# and inserts it to db. This work happens in a separate thread.
def process_node_payments(db_engine):
    session_factory = sessionmaker(bind=db_engine)

    db_session = None
    while True:
        try:
            prometheus = Prometheus()
            db_session = session_factory()

            end = datetime.datetime.utcnow()
            start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            delta = end-start

            data = json.loads(prometheus.query_rang(
                metric='keep_last_value(accountant_total_promised_amount)-' +
                'min_over_time(accountant_total_promised_amount['+str(delta.total_seconds())+'s]) > 0',
                start=start.timestamp(),
                end=end.timestamp()))
            for r in data["data"]["result"]:
                db_session.merge(PaymentTokens(r["metric"]["identity"], r["values"][-1][1]))

            db_session.commit()
            logger.info("Committed node payments batch")
        except Exception:
            logger.error("Failed to process node payments:", exc_info=True)
            if db_session is not None:
                db_session.rollback()
        finally:
            if db_session is not None:
                db_session.close()

        time.sleep(300)


def start_node_payments_worker(db_engine):
    x = threading.Thread(target=process_node_payments, args=(db_engine,), daemon=True)
    x.start()
