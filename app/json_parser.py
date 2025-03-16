import json
import random
import operator
from collections import Counter
import email.utils
from datetime import datetime

class JsonParser:
    def __init__(self, data):        
        self.input_data_dict = data
        self.topic_ids = self.input_data_dict["tid"]
        self.student_ids = list(self.input_data_dict["users"].keys())
        self.topics_counts = Counter()
        self.topic_lists = []
        self.calculate_popular_topics()
        self.student_priorities_dict = self.create_student_priorities(self.input_data_dict)
        self.topic_priorities_dict = self.create_topic_priorities(self.input_data_dict)
        self.max_accepted_proposals = int(self.input_data_dict["max_accepted_proposals"])

    def calculate_popular_topics(self):
        # Build a list of all chosen topics from each user.
        for student_id in self.student_ids:
            user_data = self.input_data_dict["users"][student_id]
            if "bids" in user_data and user_data["bids"]:
                chosen_topic_ids = [bid["tid"] for bid in user_data["bids"]]
            else:
                chosen_topic_ids = user_data.get("tid", [])
            self.topic_lists += chosen_topic_ids
        self.topics_counts = Counter(self.topic_lists)

    def create_student_priorities(self, json_dict):
        student_priorities_dict = dict()
        for student_id in self.student_ids:
            user_data = json_dict["users"][student_id]
            # If the new 'bids' array is provided, use it:
            if "bids" in user_data and user_data["bids"]:
                bids = user_data["bids"]
                # Sort bids by their 'priority' (lower value = higher preference)
                sorted_bids = sorted(bids, key=lambda bid: bid["priority"])
                chosen_topic_ids = [bid["tid"] for bid in sorted_bids]
                # Convert the timestamp strings to datetime objects and determine the latest bid time.
                timestamps = [email.utils.parsedate_to_datetime(bid["timestamp"]) for bid in bids]
                max_timestamp_dt = max(timestamps)
                max_timestamp_str = max_timestamp_dt.strftime("%a, %d %b %Y %H:%M:%S EST -05:00")
                user_data["max_timestamp"] = max_timestamp_str
            else:
                # Fallback to the old format if 'bids' is missing
                chosen_topic_ids = user_data.get("tid", [])
            
            popular_tuple = self.topics_counts.most_common(3)
            popular_topics_list = [x[0] for x in popular_tuple]

            # If no chosen topics are provided, build a default ordering.
            if not chosen_topic_ids:
                topic_already_chosen = user_data["otid"]
                all_topics = list(self.topic_ids)  # make a copy
                random.shuffle(all_topics)
                for popular_topic in popular_topics_list:
                    if popular_topic in all_topics:
                        all_topics.remove(popular_topic)
                        all_topics.append(popular_topic)
                if topic_already_chosen in all_topics:
                    all_topics.remove(topic_already_chosen)
                all_topics.append(topic_already_chosen)
                student_priorities_dict[student_id] = all_topics
                # Also add dummy 'priority' and 'time' values if needed downstream.
                user_data["priority"] = random.sample(range(1, len(all_topics)+1), len(all_topics))
                user_data["time"] = [0]
            else:
                # When chosen topics exist, sort them based on the bid priorities.
                if "bids" in user_data and user_data["bids"]:
                    chosen_topic_priorities = [bid["priority"] for bid in user_data["bids"]]
                    sorted_chosen = sorted(zip(chosen_topic_ids, chosen_topic_priorities), key=lambda x: x[1])
                    student_priorities_dict[student_id] = [tid for tid, _ in sorted_chosen]
                else:
                    chosen_topic_priorities = user_data.get("priority", [])
                    sorted_chosen = sorted(zip(chosen_topic_ids, chosen_topic_priorities), key=lambda x: x[1])
                    student_priorities_dict[student_id] = [tid for tid, _ in sorted_chosen]
                
                unchosen_topic_ids = list(set(self.topic_ids).difference(set(chosen_topic_ids)))
                topic_already_chosen = user_data["otid"]
                if topic_already_chosen in unchosen_topic_ids:
                    unchosen_topic_ids.remove(topic_already_chosen)
                random.shuffle(unchosen_topic_ids)
                for popular_topic in popular_topics_list:
                    if popular_topic in unchosen_topic_ids:
                        unchosen_topic_ids.remove(popular_topic)
                        unchosen_topic_ids.append(popular_topic)
                student_priorities_dict[student_id] += unchosen_topic_ids
                student_priorities_dict[student_id].append(topic_already_chosen)
        return student_priorities_dict

    def create_topic_priorities(self, json_dict):
        topic_priorities_dict = dict()
        for total_topic_id in self.topic_ids:
            topic_priorities_dict[total_topic_id] = []
            for student_id in self.student_ids:
                if total_topic_id in self.student_priorities_dict[student_id]:
                    user_data = json_dict["users"][student_id]
                    if "bids" in user_data and user_data["bids"]:
                        # Use the precomputed max timestamp and count from bids.
                        timestamp = user_data["max_timestamp"]
                        num_chosen_topics = len(user_data["bids"])
                    else:
                        timestamp = max(json_dict["users"][student_id]["time"]) if "time" in user_data else 0
                        num_chosen_topics = len(user_data.get("tid", []))
                    topic_priority = self.student_priorities_dict[student_id].index(total_topic_id)
                    topic_priorities_dict[total_topic_id].append((student_id, topic_priority, num_chosen_topics, timestamp))
            topic_priorities_dict[total_topic_id].sort(key=operator.itemgetter(1, 2, 3))
            topic_priorities_dict[total_topic_id] = [x for x, _, _, _ in topic_priorities_dict[total_topic_id]]
        return topic_priorities_dict
