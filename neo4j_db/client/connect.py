import logging

from neo4j import GraphDatabase

log = logging.getLogger(__name__)

def get_driver(uri="bolt://localhost:7687"):
    auth = ("neo4j", "password")
    driver = GraphDatabase.driver(uri, auth=auth)
    return driver

def ping(driver):
    driver.verify_connectivity()
    log.info("Neo4j is reachable")