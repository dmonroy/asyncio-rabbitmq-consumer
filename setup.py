from distutils.core import setup

setup(
    name='asyncio-rabbitmq-consumer',
    use_scm_version=True,
    packages=['asyncio_rabbitmq_consumer'],
    url='https://github.com/dmonroy/asyncio-rabbitmq-consumer',
    license='MIT License',
    author='Darwin Monroy',
    author_email='contact@darwinmonroy.com',
    description='Base rabbitmq consumer for asyncio',
    install_requires=[
        'aioamqp'
    ],
    setup_requires=[
        'setuptools_scm'
    ]
)
