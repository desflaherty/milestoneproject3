import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
import config
from bson.objectid import ObjectId

app = Flask(__name__)


app.config["MONGO_DBNAME"] ='CookBook'
app.config["MONGO_URI"] ='mongodb+srv://root:Allergan99@myfirstcluster-lgqe5.mongodb.net/CookBook'
#app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SECRET_KEY']="\xd4\xf3}gi\xa8fK\x87`\xbc\xea\xc5R\x81\xc1Ho\xba'\x85\xd5$\xf4"

"""
app.debug = False
if app.debug == True:
    import config
    app.config["MONGO_DBNAME"] = config.DB_CONFIG['MONGO_DBNAME']
    app.config["MONGO_URI"] = config.DB_CONFIG['MONGO_URI']
else:
    app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
"""

mongo = PyMongo(app)

users_collection = mongo.db.User_Details

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


# START OF CODE CREDIT TO 'MIROSLAV SVEC'
# CONTACTED VIA SLACK FOR ASSISTANCE
# CREATING A SESSION FOR USER REGISTRATION & LOGIN

#Login

@app.route('/login', methods=['GET'])
def login():
    # Check if user is not logged in already
    if 'user' in session:
        user_in_db = users_collection.find_one({"username": session['user']})
        if user_in_db:
            # If so redirect user to his profile
            flash("You are logged in already!")
            return redirect(url_for('profile', user=user_in_db['username']))
    else:
        # Render the page for user to be able to log in
        return render_template("login.html")

# Check user login details from login form
@app.route('/user_auth', methods=['POST'])
def user_auth():
    form = request.form.to_dict()
    user_in_db = users_collection.find_one({"username": form['username']})
    # Check for user in database
    if user_in_db:
        # If passwords match (hashed / real password)
        if check_password_hash(user_in_db['password'], form['password']):
            # Log user in (add to session)
            session['user'] = form['username']
            # If the user is admin redirect him to admin area
            #if session['user'] == "admin":
             #   return redirect(url_for('admin'))
           # else:
            flash("You were logged in!")
            return redirect(url_for('profile', user=user_in_db['username']))
        else:
            flash("Wrong password or user name!")
            return redirect(url_for('login'))
    else:
        flash("You must be registered!")
        return redirect(url_for('register'))


# Sign up
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if user is not logged in already
    if 'user' in session:
        flash('You are already signed in!')
        return redirect(url_for('index'))
    if request.method == 'POST':
        form = request.form.to_dict()
        #Check if the password and password1 actualy match 
        if form['password'] == form['password1']:
            # If so try to find the user in db
           user = users_collection.find_one({"username" : form['username']})
        if user:
          flash("{form['username']} already exists!")
          return redirect(url_for('register'))
            # If user does not exist register new user
        else:                
                # Hash password
                hash_pass = generate_password_hash(form['password'])
                #Create new user with hashed password
                users_collection.insert_one(
                    {
                        'username': form['username'],
                        'email': form['email'],
                        'password': hash_pass
                    }
                )
                # Check if user is actualy saved
                user_in_db = users_collection.find_one({"username": form['username']})
                if user_in_db:
                    # Log user in (add to session)
                    session['user'] = user_in_db['username']
                    return redirect(url_for('profile', user=user_in_db['username']))
                else:
                    flash("There was a problem saving your profile")
                    return redirect(url_for('register'))
    else:
       flash("Passwords dont match!")
       return redirect(url_for('register'))
  
       return render_template("register.html")
                    
                    
# Log out
@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You were logged out!')
    return redirect(url_for('index'))



# Admin area
#@app.route('/admin')
#def admin():
 #   if 'user' in session:
  #      if session['user'] == "admin":
   #         return render_template('admin.html')
    #    else:
     #       flash('Only Admins can access this page!')
      #      return redirect(url_for('index'))
    #else:
     #   flash('You must be logged in')
      #  return redirect(url_for('index'))                    
                    
# END OF CODE CREDIT TO 'MIROSLAV SVEC'
   
@app.route('/cuisine')
def cuisine():
    return render_template("cuisine.html", cuisine=mongo.db.Cuisine.find())    
 
    


@app.route('/recipes')
def recipes():
    return render_template("recipes.html",recipe=mongo.db.Recipe.find(),cuisine=mongo.db.Cuisine.find(),course=mongo.db.Course.find(),diet=mongo.db.Special_Diets.find()) 
    

@app.route('/recipes_sort')
def recipes_sort():
    return render_template("recipes.html", cuisine=mongo.db.Cuisine.find(),course=mongo.db.Course.find(),diet=mongo.db.Special_Diets.find(),
    recipe=mongo.db.Recipe.find().sort("recipe_likes",-1).limit(10)) 
    
    
                            
  
@app.route('/single_recipes/<recipe_id>')
def single_recipes(recipe_id):
    the_recipe =  mongo.db.Recipe.find_one({"_id": ObjectId(recipe_id)})
    return render_template("singlerecipe.html",
                            recipe=the_recipe)  
                            
 

"""
@app.route('/insert_user', methods=['POST'])
def insert_user():
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    user =  mongo.db.User_Details
    user.insert_one({"name":name,"password":password,"email":email,"username":username})
    return redirect(url_for('recipes'))
"""
    
@app.route('/add_user')    
def add_user():
     return render_template('register.html')   

"""     
@app.route('/logout')    
def logout():
     return render_template('base.html')  

"""
@app.route('/profile/<user>')
def profile(user): 
    # Check if user is logged in
    if 'user' in session:
        # If so get the user and pass him to template for now
        user_in_db = users_collection.find_one({"username": user})
        return render_template('profile.html', user=user_in_db)
    else:
        flash("You must be logged in!")
        return redirect(url_for('index'))

"""
@app.route('/my_recipes/<username>')
def my_recipes(username):
    if session['user'] == username:
        user = mongo.db.User_Details.find_one({"username": username})
        user_recipes = mongo.db.Recipe.find({"username": session['user']})
        recipe_count = user_recipes.count()

        return render_template(
            'myrecipes.html',
            user=user,
            user_recipes=user_recipes,
            recipe_count=recipe_count)

    else:
        return redirect(url_for('index'))
"""


@app.route('/add_recipes')
def add_recipes():
         return render_template('addrecipe.html',
         cuisine=mongo.db.Cuisine.find(),
         course=mongo.db.Course.find(),
         occasion=mongo.db.Occasion.find(),
         diet=mongo.db.Special_Diets.find(),
         skill=mongo.db.Skill.find())
 


    
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    recipe =  mongo.db.Recipe
    recipe.insert_one(request.form.to_dict())
    return redirect(url_for('recipes'))
    
  
  
    
@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    the_recipe =  mongo.db.Recipe.find_one({"_id": ObjectId(recipe_id)})
    all_cuisines =  mongo.db.Cuisine.find()
    all_courses =  mongo.db.Course.find()
    all_occasions =  mongo.db.Occasion.find()
    all_diets =  mongo.db.Special_Diets.find()
    all_skills =  mongo.db.Skill.find()
    return render_template('editrecipe.html', recipe=the_recipe,
                           cuisine=all_cuisines,course=all_courses,
                           occasion=all_occasions,diet=all_diets,skill=all_skills)
                           
                           
@app.route('/update_recipe/<recipe_id>', methods=["POST"])
def update_recipe(recipe_id):
    recipe = mongo.db.Recipe
    recipe.update( {'_id': ObjectId(recipe_id)},
    {
        'recipe_name':request.form.get('recipe_name'),
        'recipe_description':request.form.get('recipe_description'),
        'cuisine_name':request.form.get('cuisine_name'),
        'course_name':request.form.get('course_name'),
        'occasion_name':request.form.get('occasion_name'),
        'diet_name':request.form.get('diet_name'),
        'skill_name':request.form.get('skill_name'),
        'ingredients':request.form.get('ingredients'),
        'cook_time':request.form.get('cook_time'),
        'prep_time':request.form.get('prep_time'),
        'serves':request.form.get('serves'),
        'instruction_step_1':request.form.get('instruction_step_1'),
        'instruction_step_2':request.form.get('instruction_step_2'),
        'instruction_step_3':request.form.get('instruction_step_3'),
        'instruction_step_4':request.form.get('instruction_step_4'),
        'instruction_step_5':request.form.get('instruction_step_5'),
        'instruction_step_6':request.form.get('instruction_step_6'),
        'image':request.form.get('image'),
        'name':request.form.get('name'),
        'likes':request.form.get('recipe_likes')
    })
    return redirect(url_for('recipes'))  
    

@app.route('/delete_recipe/<recipe_id>', methods=["POST"])
def delete_recipe(recipe_id):
    mongo.db.Recipe.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('recipes'))    
 
 
                            
                             

 

@app.route("/find_multiple_categories", methods=["GET", "POST"])
def find_multiple_categories():
    cuisine = mongo.db.Cuisine.find()
    course = mongo.db.Course.find()
    diet=mongo.db.Special_Diets.find()
    if request.method == "POST":
       ingredients = request.form.get("ingredients")
       cuisine = request.form.get("cuisine_name") 
       course = request.form.get("course_name")
       diet=request.form.get("diet_name")
       mongo.db.Recipe.create_index([("$**", "text")])
       recipes= mongo.db.Recipe.find({"$text": {"$search": ingredients }})
       
       
       
       
       if course and not cuisine and not ingredients and not diet:
         recipes= mongo.db.Recipe.find({"course_name" :course})
         
       elif cuisine and not course  and not ingredients and not diet:
         recipes= mongo.db.Recipe.find({"cuisine_name" :cuisine})
         
         
       elif diet and not course and not cuisine and not ingredients:
         recipes= mongo.db.Recipe.find({"diet_name" :diet}) 
         
       elif ingredients and not course and not cuisine and not diet:
            recipes= mongo.db.Recipe.find({"$text": {"$search": ingredients }})
          
          
       elif course and cuisine and not ingredients and not diet:
              recipes = mongo.db.Recipe.find({"$and": [{"cuisine_name": cuisine}, {"course_name": course}] }) 
          
       elif ingredients and cuisine and not course and not diet:
               recipes = mongo.db.Recipe.find({"$and": [{"cuisine_name": cuisine}, {
                                           "$text": {"$search": ingredients }} ] })   
       
       elif ingredients and course and not cuisine and not diet:
               recipes = mongo.db.Recipe.find({"$and": [{"course_name": course}, {
                                           "$text": {"$search": ingredients }} ] })  
       
       elif ingredients and diet and not cuisine and not course:
               recipes = mongo.db.Recipe.find({"$and": [{"diet_name": diet}, {
                                           "$text": {"$search": ingredients }} ] })
                                           
       elif ingredients and diet and cuisine and not course:
               recipes = mongo.db.Recipe.find({"$and": [{"diet_name": diet},{"cuisine_name": cuisine}, {
                                           "$text": {"$search": ingredients }} ] })  
                                           
       elif ingredients and diet and course and not cuisine:
               recipes = mongo.db.Recipe.find({"$and": [{"diet_name": diet},{"course_name": course}, {
                                           "$text": {"$search": ingredients }} ] })                                     
                                           
       
       elif diet and course and cuisine and not ingredients:
              recipes = mongo.db.Recipe.find({"$and": [{"cuisine_name": cuisine}, {"course_name": course}, {"diet_name" :diet} ]})
              
       elif diet and cuisine and not course and not ingredients:
              recipes = mongo.db.Recipe.find({"$and": [{"cuisine_name": cuisine}, {"diet_name" :diet} ]})      
       
       
       elif diet and course and not cuisine and not ingredients:
              recipes = mongo.db.Recipe.find({"$and": [{"course_name": course}, {"diet_name" :diet} ]})  
                                           
       elif ingredients and cuisine and course and not diet:
           recipes = mongo.db.Recipe.find({"$and": [{"cuisine_name": cuisine}, {"course_name": course}, {
                                           "$text": {"$search": ingredients }} ] }) 
                                           
       elif ingredients and cuisine and course and diet:
           recipes = mongo.db.Recipe.find({"$and": [{"cuisine_name": cuisine}, {"course_name": course},{"diet_name" :diet}, {
                                           "$text": {"$search": ingredients }} ] })     
                                           
    recipe_count = recipes.count()                                   
                                           
    return render_template('filter_recipes.html',recipe=recipes,ingredients=ingredients,cuisine=cuisine,course=course,diet=diet,recipe_count=recipe_count)



if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)