import app.models as models
import app.utils.database as database
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session


def get_statuses(query_params):
    statuses = []
    model = models.ChannelStatus
    query = select(model)

    query = filter_on_batch_reference(query, query_params)
    query = filter_on_nhs_number(query, query_params)
    query = filter_on_created_at(query, query_params)
    query = filter_on_status_clause(query, query_params)

    logging.debug("Query: %s", query)

    try:
        with Session(database.engine()) as session:
            statuses = session.scalars(query).all()
    except Exception as e:
        logging.error("Error getting statuses: %s",  e)

    return statuses


def filter_on_batch_reference(query, query_params):
    if query_params.get("batchReference"):
        query = query.join(
            models.Message, models.Message.message_id == models.ChannelStatus.message_id
        ).join(
            models.MessageBatch, models.MessageBatch.id == models.Message.batch_id
        ).where(
            models.MessageBatch.batch_reference == query_params.get("batchReference")
        )

    return query


def filter_on_nhs_number(query, query_params):
    if query_params.get("nhsNumber"):
        query = query.join(
            models.Message, models.Message.message_id == models.ChannelStatus.message_id
        ).where(
            models.Message.nhs_number == query_params.get("nhsNumber")
        )

    return query


def filter_on_created_at(query, query_params):
    if query_params.get("createdAfter"):
        query = query.where(
            models.ChannelStatus.created_at > query_params.get("createdAfter"))

    if query_params.get("createdBefore"):
        query = query.where(
            models.ChannelStatus.created_at < query_params.get("createdBefore"))

    return query


def filter_on_status_clause(query, query_params):
    if query_params.get("channel"):
        query = query.where(
            models.ChannelStatus.details["data", 0, "attributes", "channel"].astext == query_params.get("channel"))

        if query_params.get("channelStatus"):
            query = query.where(
                models.ChannelStatus.details["data", 0, "attributes", "channelStatus"].astext == query_params.get("channelStatus"))

        if query_params.get("supplierStatus"):
            query = query.where(
                models.ChannelStatus.details["data", 0, "attributes", "supplierStatus"].astext == query_params.get("supplierStatus"))

    return query
