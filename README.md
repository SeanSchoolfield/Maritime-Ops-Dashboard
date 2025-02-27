# Kafka Development

We will run Kafka in KRaft mode. I think it works better with scalability, and reduces heirarchical dependency that Zookeeper typically deploys.

## Setting up Kafka

### Download Kafka
Download the Kafka package [here](https://www.apache.org/dyn/closer.cgi?path=/kafka/3.9.0/kafka_2.13-3.9.0.tgz). Unpack it, and navigate into the directory.

### Starting Environment
Generate a cluster UUID
```bash
$ KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
```
Format the log directory
```bash
$ bin/kafka-storage.sh format --standalone -t $KAFKA_CLUSTER_ID -c config/kraft/reconfig-server.properties
```
Start the Kafka Server
```bash
$ bin/kafka-server-start.sh config/kraft/reconfig-server.properties
```
This will serve as your broker/server, so leave this console open.

## Creating a Topic
These commands will be run in a new console window. They are all assumed to be in the same Kafka directory you downloaded and unpackaged.

### Initialize new topic
```bash
$ bin/kafka-topics.sh --create --topic [topic-name] --bootstrap-server localhost:9092
```

### Listing full topic details
Enter the following to list all topics and corresponding metadata on the connected server.
```bash
$ bin/kafka-topics.sh --describe --topic quickstart-events --bootstrap-server localhost:9092
```
## Launching Producer console
Run the following command
```bash
$ bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic [topic] --property parse.key=true --property key.seperator=:
```
This opens a console for you to enter data that will then be pushed to the topic as an event. This expects a key-value pair, with ':' as a delimiter. Each newline denotes a new message. [Ctrl-C] to exit and commit events.

## Launching Consumer console 
Run the following command
```bash
$ bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic [topic] --from-beginning --property print.timestamp=true --property print.key=true property print.value=true6
```
Prints events previously committed to topic, and provides a live feed of events that continue to be pushed.
