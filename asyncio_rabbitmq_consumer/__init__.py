import asyncio
import logging
import aioamqp

log = logging.getLogger()

DEFAULT_EXCHANGE_TYPE = 'direct'
DEFAULT_RABBIT_URL = 'amqp://localhost:5672/'


class Consumer(object):

    def __init__(self, queue_name, exchange_name=None,
                 exchange_type=DEFAULT_EXCHANGE_TYPE, routing_key='',
                 rabbit_url=DEFAULT_RABBIT_URL, loop=None):

        self._exchange_name = exchange_name
        self._exchange_type = exchange_type
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._url = rabbit_url
        self.loop = loop

        self._transport = None
        self._protocol = None
        self._channel = None

        self.on_error = None

    @asyncio.coroutine
    def connect(self):
        try:
            self._transport, self._protocol = \
                yield from aioamqp.from_url(
                    self._url,
                    on_error=self.on_error,
                    loop=self.loop
                )
        except aioamqp.AmqpClosedConnection as e:
            log.exception(e)
            return

    @asyncio.coroutine
    def finish(self):
        yield from self._channel.close()

    @asyncio.coroutine
    def start_consuming(self, on_message, on_error):
        self.on_error = on_error

        yield from self.connect()

        self._channel = yield from self._protocol.channel()

        yield from self.declare_exchange()
        yield from self.declare_queue()
        yield from self.bind_queue()

        yield from self._channel.basic_consume(
            on_message,
            queue_name=self._queue_name
        )

    @asyncio.coroutine
    def declare_exchange(self):
        yield from self._channel.exchange_declare(
            exchange_name=self._exchange_name,
            type_name=self._exchange_type,
            durable=True
        )

    @asyncio.coroutine
    def declare_queue(self):
        yield from self._channel.queue(
            queue_name=self._queue_name,
            durable=True
        )

    @asyncio.coroutine
    def bind_queue(self):
        yield from self._channel.queue_bind(
            exchange_name=self._exchange_name,
            queue_name=self._queue_name,
            routing_key=self._routing_key
        )

    @asyncio.coroutine
    def acknowledge_message(self, delivery_tag):
        log.debug('ACK {}'.format(delivery_tag))
        yield from self._channel.basic_client_ack(
            delivery_tag=delivery_tag
        )

    @asyncio.coroutine
    def reject_message(self, delivery_tag, requeue=True):
        log.debug('NACK {}'.format(delivery_tag))
        yield from self._channel.basic_client_nack(
            delivery_tag=delivery_tag, requeue=requeue
        )
