#!/usr/bin/env python3

import argparse
import os
import re
import shutil
from typing import Text

import rosbag
import termcolor

pattern = "/[0-9]"


def rename(input_bag_path: Text, prefix: Text):
    to_be_renamed = _check_topic_name_in_bag(input_bag_path)
    if to_be_renamed:
        print("Starting bag rebuild. Please wait.")
        _save_renamed_bag(input_bag_path, prefix)
        print("done")
    else:
        print(termcolor.colored("input_bag has no invalid topic name.", "green"))


def _check_topic_name_in_bag(input_bag_path: Text) -> bool:
    input_bag = rosbag.Bag(input_bag_path, "r")
    bag_info = input_bag.get_type_and_topic_info()
    topics_in_bag = bag_info.topics
    for topic_name in topics_in_bag:
        res = re.search(pattern, topic_name)
        if res is not None:
            # found at least 1, then input bag to be rebuilt
            print("found invalid topic name: " + topic_name)
            return True
    return False


def _save_renamed_bag(input_bag_path: Text, prefix: Text):
    # rename input bag
    input_work_path = os.path.join(
        os.path.dirname(input_bag_path), "work_" + os.path.basename(input_bag_path)
    )
    shutil.move(input_bag_path, input_work_path)
    # open bags
    inbag = rosbag.Bag(input_work_path, "r")
    outbag = rosbag.Bag(input_bag_path, "w")

    for topic, msg, t in inbag.read_messages():
        res = re.search(pattern, topic)
        if res is not None:
            index = res.start()
            # index is positition at /, insert prefix after /
            topic = topic[: index + 1] + prefix + topic[index + 1 :]
        # write same msg from input bag
        outbag.write(topic, msg, t)
    outbag.close()
    inbag.close()
    # delete inbag
    os.remove(input_work_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="rename invalid topic names in bag")
    parser.add_argument("-i", "--input_bag", required=True, help="input bag file")
    parser.add_argument(
        "-p",
        "--prefix",
        required=True,
        help="prefix to be added before the invalid topic name token",
    )
    args = parser.parse_args()
    rename(os.path.expandvars(args.input_bag), args.prefix)
