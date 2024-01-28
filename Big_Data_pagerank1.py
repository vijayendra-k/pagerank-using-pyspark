# -*- coding: utf-8 -*-
"""Assignment 1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11_o4N6Cp9R8VnAA-kK4RHo9pv_CHZ3mS
"""

!apt-get install openjdk-8-jdk-headless -qq > /dev/null
!wget -q https://archive.apache.org/dist/spark/spark-3.2.0/spark-3.2.0-bin-hadoop3.2.tgz
!tar xf /content/spark-3.2.0-bin-hadoop3.2.tgz
!pip install -q findspark
!pip install pyspark
import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.2.0-bin-hadoop3.2"

import findspark
findspark.init()
from pyspark import SparkContext
from google.colab import files
files.upload()

sc = SparkContext.getOrCreate()
rdd0 = sc.textFile("pagerank_bigdata.txt")
print(rdd0.collect())
def parseLinks(line):
  linelist = [x for x in line.split(" ")]
  return (linelist[0], linelist[1:])

rdd1 = rdd0.map(lambda line : parseLinks(line))
partitionedrdd = rdd1.partitionBy(3, lambda key: hash(key))
print(rdd1.collect())

alpha=0.75
N=rdd1.count()
initialpagerank=1.0/N
delta=0
threshold = 0.0001
pagerankrdd = rdd1.map(lambda line : (line[0], initialpagerank))
print(pagerankrdd.collect())

def evalpagerank(line,deltaval):
  initialpagerank= (alpha/N) + (deltaval/N + line[1])*(1 - alpha)
  return ((line[0], initialpagerank))


def findpagerank(node):
    returnlist = []
    parent_node, parent_node_rank_value, child_node_list = node[0], node[1][0], node[1][1]
    no_of_child_nodes = len(child_node_list)
    for child_node in child_node_list:
        child_rank_value = parent_node_rank_value / no_of_child_nodes
        returnlist.append((child_node, child_rank_value))
    return returnlist

from operator import add, sub
def calculate_abs_diff(line):
    return line

def filter_above_threshold(line):
    return abs(line[1]) > threshold

def isconvergent(prevrdd, newrdd):
    global threshold
    abs_diff = (prevrdd.union(newrdd)).map(calculate_abs_diff).reduceByKey(sub)
    abovethreshold = abs_diff.filter(filter_above_threshold)
    if abovethreshold.count() < 1:
        return abs_diff, 1
    else:
        return abs_diff, 0

'''
Dangle node section
'''
def checkdelta(line):
  if (len(line[1][1])==0):
    return line[1][0]
  else:
    return 0

i=1
while (i<25):
  print("\nPage Ranks in",i,"th iteration: ",pagerankrdd.collect())
  mergedrdd = pagerankrdd.join(partitionedrdd)
  newdelta = mergedrdd.map(lambda line: checkdelta(line)).reduce(add)
  print("New Delta:",newdelta)
  rankvaluesofrdd = mergedrdd.flatMap(lambda line: findpagerank(line)).reduceByKey(add)
  oldranks = pagerankrdd
  pagerankrdd = rankvaluesofrdd.map(lambda line: evalpagerank(line,delta))
  abslist, convergence = isconvergent(oldranks, pagerankrdd)
  print("Absolute difference:",abslist.collect())
  if convergence:
    break
  i=i+1

sortedrdd = pagerankrdd.sortBy(lambda x:x[1])
print("Final page ranks:",sortedrdd.collect())
print("Is Convergence found?",convergence)