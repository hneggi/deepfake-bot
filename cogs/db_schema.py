from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

Base = declarative_base()


class Trainer(Base):
    """Bot users"""
    __tablename__ = 'trainers'
    id = Column(BigInteger, primary_key=True)
    discord_id = Column(BigInteger, unique=True)
    user_name = Column(String(255, collation='utf8_general_ci'))
    time_registered = Column(DateTime)
    subscribed = Column(Boolean)


class Subject(Base):
    """Training subjects, i.e. discord users on a particular server who we will convert into models"""
    __tablename__ = 'subjects'
    id = Column(BigInteger, primary_key=True)
    discord_id = Column(BigInteger)
    trainer_id = Column(BigInteger)
    subject_name = Column(String(255, collation='utf8_general_ci'))
    server_id = Column(BigInteger)
    server_name = Column(String(255, collation='utf8_general_ci'))


class DataSet(Base):
    """Collected chat logs of our subjects"""
    __tablename__ = 'data_sets'
    id = Column(BigInteger, primary_key=True)
    subject_id = Column(BigInteger, ForeignKey('subjects.id'))
    subject_foreign_key = relationship('Subject', foreign_keys=[subject_id])

    # data_uid is the file name stored in an S3 container. Expires after 30 days.
    time_collected = Column(DateTime)
    data_uid = Column(String(32, collation='utf8_general_ci'), unique=True)


class TextFilter(Base):
    """Text filters we apply to our data sets"""
    __tablename__ = 'filters'
    id = Column(BigInteger, primary_key=True)
    subject_id = Column(BigInteger, ForeignKey('subjects.id'))
    subject_foreign_key = relationship('Subject', foreign_keys=[subject_id])
    word = Column(String(255, collation='utf8_general_ci'))


class MarkovSettings(Base):
    """State size and newline options that will get applied to subject's model"""
    __tablename__ = 'markov_settings'
    id = Column(BigInteger, primary_key=True)
    subject_id = Column(BigInteger, ForeignKey('subjects.id'))
    subject_foreign_key = relationship('Subject', foreign_keys=[subject_id])
    state_size = Column(Integer)
    newline = Column(Boolean)


class MarkovModel(Base):
    """Markov chain models generated from our subject's chat history"""
    __tablename__ = 'markov_models'
    id = Column(BigInteger, primary_key=True)
    data_set_id = Column(BigInteger, ForeignKey('data_sets.id'))
    data_set_foreign_key = relationship('DataSet', foreign_keys=[data_set_id])

    # Works similar to data sets. Stored in S3 with 30 day expiration
    time_collected = Column(DateTime)
    model_uid = Column(String(32), unique=True)


class Deployment(Base):
    """An encrypted markov chain model, that is either hosted by us or the user"""
    __tablename__ = 'deployments'
    id = Column(BigInteger, primary_key=True)

    # Used for encryption
    secret_key = Column(String(255))
    markov_id = Column(BigInteger, ForeignKey('markov_models.id'))
    markov_foreign_key = relationship('MarkovModel', foreign_keys=[markov_id])

    # A deployment must be owned by a specific trainer
    trainer_id = Column(BigInteger, ForeignKey('trainers.id'))
    trainer_foreign_key = relationship('Trainer', foreign_keys=[trainer_id])

    # Not hosted for self-deployed bots
    hosted = Column(Boolean)


class HostedDeployment(Base):
    """A trained bot running on an ECS container"""
    __tablename__ = 'hosted_deployments'
    id = Column(BigInteger, primary_key=True)
    deployment_id = Column(BigInteger, ForeignKey('deployments.id'))
    deployment_foreign_key = relationship('Deployment', foreign_keys=[deployment_id])

    # Discord Credentials
    bot_token = Column(String(255, collation='utf8_general_ci'))

    # Container management
    status = Column(String(255, collation='utf8_general_ci'))
    heartbeat = Column(DateTime)
    expiration = Column(DateTime)


class HostedBotSettings(Base):
    """Users can configure their bots with these"""
    __tablename__ = 'hosted_bot_settings'
    id = Column(BigInteger, primary_key=True)
    hosted_deployment_id = Column(BigInteger, ForeignKey('hosted_deployments.id'))
    hosted_deployment_foreign_key = relationship('HostedDeployment', foreign_keys=[hosted_deployment_id])

    reply_probability = Column(Float)
    new_conversation_min_wait = Column(Integer)
    new_conversation_max_wait = Column(Integer)
    max_sentence_length = Column(Integer)
    max_markov_chains = Column(Integer)
    selection_algorithm = Column(String(255, collation='utf8_general_ci'))
    quiet_mode = Column(Boolean)
    avg_delay = Column(Float)
    std_dev_delay = Column(Float)
    min_delay = Column(Float)
    avg_typing_speed = Column(Float)
    std_dev_typing_speed = Column(Float)
    min_typing_speed = Column(Float)
    bot_prefix = Column(String(255, collation='utf8_general_ci'))
