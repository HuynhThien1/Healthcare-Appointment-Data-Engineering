from pyspark.sql.functions import (
    lit,
    when
)


def map_notification_event_type(action_col):
    return (
        when(action_col == "BOOKED", lit("BOOKING_CONFIRMATION"))
        .when(action_col == "CANCELLED", lit("BOOKING_CANCELLATION"))
        .otherwise(lit(None))
    )