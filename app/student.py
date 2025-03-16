class Student:
    def __init__(self, model, id, choices):
        self.model = model
        self.id = id
        self.choices = choices
        self.num_remaining_slots = self.model.max_accepted_proposals
        self.proposals = []           # instance variable
        self.accepted_proposals = []  # instance variable

    def receive_proposal(self, topic_id):
        self.proposals.append(topic_id)

    def accept_proposal(self):
        # Remove duplicates
        temp = []
        for x in self.proposals:
            if x not in temp:
                temp.append(x)
        self.proposals = temp
        # Sort proposals based on student's choices
        self.proposals.sort(key=lambda proposal: self.choices.index(proposal))
        if self.num_remaining_slots > 0:
            self.accepted_proposals += self.proposals[:self.num_remaining_slots]
            self.num_remaining_slots -= len(self.accepted_proposals)
        self.proposals = []  # clear proposals
        for topic_id in self.accepted_proposals:
            self.model.get_topic(topic_id).update_accepted_proposals(self.id)
        self.num_remaining_slots -= len(self.accepted_proposals)
