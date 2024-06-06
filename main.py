from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from datetime import datetime
import logging

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb+srv://Kavan04:Wings123@cluster0.bpjc6jr.mongodb.net/mydatabase?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Set up logging
logging.basicConfig(level=logging.INFO)


@app.route('/projects', methods=['POST'])
def add_project():
    logging.info("POST /projects called")
    
    data = request.json
    if not data:
        logging.error("No data provided")
        return jsonify({"error": "No data provided"}), 400
    
    required_fields = ["name", "description", "date_done", "tags"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        logging.error(f"Missing fields: {', '.join(missing_fields)}")
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400
    
    try:
        data['date_done'] = datetime.strptime(data['date_done'], '%Y-%m-%d')
    except ValueError:
        logging.error("Invalid date format")
        return jsonify({"error": "Invalid date format, should be YYYY-MM-DD"}), 400
    
    try:
        result = mongo.db.projects.insert_one(data)
        logging.info(f"Inserted ID: {str(result.inserted_id)}")
        return jsonify({"result": str(result.inserted_id)}), 201
    except Exception as e:
        logging.error(f"Error inserting data: {str(e)}")
        return jsonify({"error": "An error occurred while inserting data"}), 500




@app.route('/projects', methods=['GET'])
def get_projects():
    logging.info("GET /projects called")
    query = {}
    
    name = request.args.get('name')
    if name:
        query['name'] = {"$regex": name, "$options": "i"}
    
    description = request.args.get('description')
    if description:
        query['description'] = {"$regex": description, "$options": "i"}
    
    date_done = request.args.get('date_done')
    if date_done:
        try:
            date_done = datetime.strptime(date_done, '%Y-%m-%d')
            query['date_done'] = date_done
        except ValueError:
            logging.error("Invalid date format")
            return jsonify({"error": "Invalid date format, should be YYYY-MM-DD"}), 400
    
    tags = request.args.getlist('tags')
    if tags:
        query['tags'] = {"$all": tags}
    
    sort_by = request.args.get('sort_by', 'date_done')
    sort_order = request.args.get('sort_order', 'asc')
    sort_order = -1 if sort_order == 'desc' else 1
    
    try:
        projects = mongo.db.projects.find(query).sort(sort_by, sort_order)
        return dumps(projects), 200
    except Exception as e:
        logging.error(f"Error fetching data: {str(e)}")
        return jsonify({"error": "An error occurred while fetching data"}), 500

@app.route('/projects/<id>', methods=['GET'])
def get_project(id):
    logging.info(f"GET /projects/{id} called")
    try:
        project = mongo.db.projects.find_one({"_id": ObjectId(id)})
        if project:
            return dumps(project), 200
        else:
            logging.error("Project not found")
            return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        logging.error(f"Error fetching data: {str(e)}")
        return jsonify({"error": "Invalid ID format or an error occurred while fetching data"}), 400



@app.route('/projects/<id>', methods=['PUT'])
def update_project(id):
    logging.info(f"PUT /projects/{id} called")
    data = request.json
    if not data:
        logging.error("No data provided")
        return jsonify({"error": "No data provided"}), 400
    
    try:
        if 'date_done' in data:
            data['date_done'] = datetime.strptime(data['date_done'], '%Y-%m-%d')
    except ValueError:
        logging.error("Invalid date format")
        return jsonify({"error": "Invalid date format, should be YYYY-MM-DD"}), 400
    
    try:
        result = mongo.db.projects.update_one({"_id": ObjectId(id)}, {"$set": data})
        if result.matched_count:
            logging.info("Project updated")
            return jsonify({"result": "Project updated"}), 200
        else:
            logging.error("Project not found")
            return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        logging.error(f"Error updating data: {str(e)}")
        return jsonify({"error": "Invalid ID format or an error occurred while updating data"}), 400



@app.route('/projects/<id>', methods=['DELETE'])
def delete_project(id):
    logging.info(f"DELETE /projects/{id} called")
    try:
        result = mongo.db.projects.delete_one({"_id": ObjectId(id)})
        if result.deleted_count:
            logging.info("Project deleted")
            return jsonify({"result": "Project deleted"}), 200
        else:
            logging.error("Project not found")
            return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        logging.error(f"Error deleting data: {str(e)}")
        return jsonify({"error": "Invalid ID format or an error occurred while deleting data"}), 400

@app.route('/', methods=['GET'])
def home():
    logging.info("GET / called")
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)
