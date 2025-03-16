#!flask/bin/python
from flask import Flask, jsonify,request
from . import json_parser, topics_matcher

app = Flask(__name__)

@app.route('/match_topics', methods=['POST'])
def topic_matching():
    # Attempt to get JSON from the request without forcing an error.
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Bad Request", "message": "No JSON input provided"}), 400

    # Try to parse the input.
    try:
        input_parsed_model = json_parser.JsonParser(data)
    except Exception as e:
        return jsonify({
            "error": "Bad Request",
            "message": f"Invalid input: {str(e)}"
        }), 400

    # Try to run the matching algorithm.
    try:
        assigned_topics_model = topics_matcher.TopicsMatcher(
            input_parsed_model.student_ids,
            input_parsed_model.topic_ids,
            input_parsed_model.student_priorities_dict,
            input_parsed_model.topic_priorities_dict,
            input_parsed_model.max_accepted_proposals
        )
        result = assigned_topics_model.get_student_topic_matches()
    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "message": f"An error occurred during matching: {str(e)}"
        }), 500

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True)