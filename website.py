from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import json
import os
import socket

app = FastAPI(title="FlavorFinds", version="2.0")

# Create data directory for feedback
os.makedirs("data", exist_ok=True)


# ---------- Data Models ----------
class Recipe(BaseModel):
    id: int
    name: str
    type: str
    time: str
    rating: float
    img: str
    desc: str
    ingredients: List[str]
    steps: List[str]
    difficulty: str = "Easy"
    calories: Optional[int] = None
    tags: List[str] = []


class Feedback(BaseModel):
    name: str
    email: str
    rating: int
    message: str
    recipe_id: Optional[int] = None
    timestamp: str


# ---------- Enhanced Sample Data with More Recipes ----------
recipes_db = [
    # Breakfast Recipes
    Recipe(
        id=1,
        name="Classic Pancakes",
        type="Breakfast",
        time="20 min",
        rating=4.7,
        img="https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=300",
        desc="Fluffy golden pancakes with maple syrup and fresh berries.",
        ingredients=["2 cups flour", "1 cup milk", "2 eggs", "2 tbsp sugar", "1 tbsp baking powder",
                     "1 tsp vanilla extract"],
        steps=["Mix dry ingredients", "Add wet ingredients", "Whisk until smooth", "Cook on medium heat",
               "Flip when bubbles form", "Serve with syrup"],
        difficulty="Easy",
        calories=320,
        tags=["vegetarian", "quick", "family-friendly", "sweet"]
    ),
    Recipe(
        id=2,
        name="Avocado Toast",
        type="Breakfast",
        time="10 min",
        rating=4.5,
        img="https://images.unsplash.com/photo-1541519227354-08fa5d50c44d?w=300",
        desc="Healthy smashed avocado on sourdough with seasonings.",
        ingredients=["2 slices sourdough bread", "1 ripe avocado", "1 lime", "salt", "pepper", "red pepper flakes",
                     "olive oil"],
        steps=["Toast bread until golden", "Mash avocado with lime juice", "Season with salt and pepper",
               "Spread on toast", "Drizzle with olive oil"],
        difficulty="Easy",
        calories=280,
        tags=["vegan", "healthy", "quick", "gluten-free"]
    ),
    Recipe(
        id=3,
        name="French Toast",
        type="Breakfast",
        time="15 min",
        rating=4.6,
        img="https://images.unsplash.com/photo-1484723091739-30a097e8f929?w=300",
        desc="Golden brown French toast with cinnamon and maple syrup.",
        ingredients=["4 slices bread", "2 eggs", "1/2 cup milk", "1 tsp cinnamon", "1 tsp vanilla", "2 tbsp butter"],
        steps=["Whisk eggs, milk, cinnamon, vanilla", "Dip bread slices", "Cook in butter until golden",
               "Serve with syrup"],
        difficulty="Easy",
        calories=350,
        tags=["sweet", "comfort-food", "family"]
    ),
    Recipe(
        id=4,
        name="Vegetable Omelette",
        type="Breakfast",
        time="15 min",
        rating=4.4,
        img="https://images.unsplash.com/photo-1551782450-17144efb9c50?w=300",
        desc="Fluffy omelette filled with fresh vegetables and cheese.",
        ingredients=["3 eggs", "1/4 cup bell peppers", "1/4 cup onions", "1/4 cup mushrooms", "1/4 cup cheese", "salt",
                     "pepper"],
        steps=["Chop vegetables", "Whisk eggs with seasoning", "Cook vegetables", "Add eggs and cook",
               "Fold and serve"],
        difficulty="Medium",
        calories=280,
        tags=["protein", "healthy", "low-carb"]
    ),

    # Lunch Recipes
    Recipe(
        id=5,
        name="Caesar Salad",
        type="Lunch",
        time="15 min",
        rating=4.3,
        img="https://images.unsplash.com/photo-1546793665-c74683f339c1?w=300",
        desc="Classic Caesar salad with crispy romaine and homemade dressing.",
        ingredients=["Romaine lettuce", "Parmesan cheese", "Croutons", "Anchovies", "Lemon juice", "Olive oil",
                     "Garlic"],
        steps=["Chop lettuce", "Make dressing", "Toss with croutons", "Add Parmesan", "Serve immediately"],
        difficulty="Easy",
        calories=320,
        tags=["healthy", "fresh", "quick-lunch"]
    ),
    Recipe(
        id=6,
        name="Chicken Wrap",
        type="Lunch",
        time="10 min",
        rating=4.5,
        img="https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300",
        desc="Grilled chicken wrap with fresh vegetables and sauce.",
        ingredients=["Tortilla wrap", "Grilled chicken", "Lettuce", "Tomato", "Cucumber", "Mayonnaise", "Cheese"],
        steps=["Warm tortilla", "Layer ingredients", "Roll tightly", "Cut in half", "Serve"],
        difficulty="Easy",
        calories=380,
        tags=["protein", "portable", "quick"]
    ),
    Recipe(
        id=7,
        name="Quinoa Bowl",
        type="Lunch",
        time="20 min",
        rating=4.6,
        img="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300",
        desc="Nutritious quinoa bowl with roasted vegetables and tahini dressing.",
        ingredients=["Quinoa", "Sweet potato", "Broccoli", "Chickpeas", "Tahini", "Lemon", "Olive oil"],
        steps=["Cook quinoa", "Roast vegetables", "Make dressing", "Combine all ingredients", "Garnish with herbs"],
        difficulty="Medium",
        calories=420,
        tags=["vegan", "healthy", "meal-prep"]
    ),

    # Dinner Recipes
    Recipe(
        id=8,
        name="Spaghetti Carbonara",
        type="Dinner",
        time="30 min",
        rating=4.8,
        img="https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=300",
        desc="Creamy Italian pasta with crispy bacon and Parmesan cheese.",
        ingredients=["400g spaghetti", "200g bacon", "3 eggs", "100g Parmesan", "black pepper", "garlic"],
        steps=["Cook pasta", "Fry bacon until crispy", "Mix eggs and cheese", "Combine everything off heat",
               "Add pepper"],
        difficulty="Medium",
        calories=450,
        tags=["pasta", "italian", "comfort-food", "creamy"]
    ),
    Recipe(
        id=9,
        name="Grilled Salmon",
        type="Dinner",
        time="25 min",
        rating=4.7,
        img="https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=300",
        desc="Perfectly grilled salmon with lemon and herbs.",
        ingredients=["Salmon fillets", "Lemon", "Olive oil", "Garlic", "Dill", "Salt", "Pepper"],
        steps=["Season salmon", "Preheat grill", "Grill 4-6 minutes per side", "Squeeze lemon", "Garnish with dill"],
        difficulty="Medium",
        calories=350,
        tags=["seafood", "healthy", "protein", "low-carb"]
    ),
    Recipe(
        id=10,
        name="Beef Stir Fry",
        type="Dinner",
        time="20 min",
        rating=4.4,
        img="https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=300",
        desc="Quick and flavorful beef stir fry with vegetables.",
        ingredients=["Beef strips", "Bell peppers", "Broccoli", "Soy sauce", "Ginger", "Garlic", "Sesame oil"],
        steps=["Slice beef and vegetables", "Stir-fry beef", "Add vegetables", "Add sauce", "Serve over rice"],
        difficulty="Medium",
        calories=380,
        tags=["asian", "quick", "protein-rich"]
    ),
    Recipe(
        id=11,
        name="Vegetable Curry",
        type="Dinner",
        time="35 min",
        rating=4.5,
        img="https://images.unsplash.com/photo-1455855748-9c949ab5daf1?w=300",
        desc="Spicy vegetable curry with coconut milk and aromatic spices.",
        ingredients=["Mixed vegetables", "Coconut milk", "Curry paste", "Onion", "Garlic", "Ginger", "Basil"],
        steps=["Sauté onions", "Add curry paste", "Add vegetables", "Add coconut milk", "Simmer until tender"],
        difficulty="Medium",
        calories=320,
        tags=["vegan", "spicy", "comfort-food"]
    ),

    # Dessert Recipes
    Recipe(
        id=12,
        name="Chocolate Brownies",
        type="Dessert",
        time="45 min",
        rating=4.9,
        img="https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=300",
        desc="Rich, fudgy chocolate brownies with walnuts.",
        ingredients=["Butter", "Sugar", "Eggs", "Flour", "Cocoa powder", "Chocolate chips", "Walnuts"],
        steps=["Melt butter and chocolate", "Mix ingredients", "Bake at 350°F", "Cool before cutting"],
        difficulty="Easy",
        calories=420,
        tags=["chocolate", "sweet", "baking"]
    ),
    Recipe(
        id=13,
        name="Berry Cheesecake",
        type="Dessert",
        time="4 hours",
        rating=4.8,
        img="https://images.unsplash.com/photo-1567306301408-9b74779a11af?w=300",
        desc="Creamy cheesecake with fresh berry topping.",
        ingredients=["Cream cheese", "Sugar", "Eggs", "Graham crackers", "Butter", "Mixed berries", "Whipped cream"],
        steps=["Make crust", "Prepare filling", "Bake in water bath", "Chill overnight", "Add berry topping"],
        difficulty="Hard",
        calories=380,
        tags=["cheesecake", "berries", "special-occasion"]
    ),
    Recipe(
        id=14,
        name="Apple Pie",
        type="Dessert",
        time="1 hour",
        rating=4.7,
        img="https://images.unsplash.com/photo-1535920527002-b35e96722206?w=300",
        desc="Classic American apple pie with cinnamon and nutmeg.",
        ingredients=["Apples", "Pie crust", "Sugar", "Cinnamon", "Nutmeg", "Butter", "Lemon juice"],
        steps=["Peel and slice apples", "Mix with spices", "Fill pie crust", "Bake until golden",
               "Cool before serving"],
        difficulty="Medium",
        calories=350,
        tags=["pie", "classic", "baking"]
    ),
    Recipe(
        id=15,
        name="Tiramisu",
        type="Dessert",
        time="6 hours",
        rating=4.9,
        img="https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=300",
        desc="Classic Italian tiramisu with coffee and mascarpone.",
        ingredients=["Ladyfingers", "Coffee", "Mascarpone", "Eggs", "Sugar", "Cocoa powder"],
        steps=["Brew strong coffee", "Make mascarpone cream", "Layer ladyfingers and cream", "Dust with cocoa",
               "Chill for 6 hours"],
        difficulty="Hard",
        calories=320,
        tags=["italian", "coffee", "no-bake"]
    )
]

# ---------- Frontend HTML with Enhanced Features ----------
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>FlavorFinds - Discover Amazing Recipes</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
  <style>
    :root {
      --primary: #ff7043;
      --secondary: #4caf50;
      --dark: #333;
      --light: #f5f5f5;
      --shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
      min-height: 100vh;
    }

    /* Header Styles */
    header {
      background: linear-gradient(135deg, var(--primary), #ff8a65);
      color: white;
      padding: 1.5rem 1rem;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }

    .header-content {
      position: relative;
      z-index: 2;
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 1.8rem;
      font-weight: bold;
    }

    .logo i {
      font-size: 2rem;
    }

    /* Search and Filter Section */
    .controls {
      background: white;
      padding: 1rem;
      margin: 1rem;
      border-radius: 10px;
      box-shadow: var(--shadow);
      max-width: 1200px;
      margin: 1rem auto;
    }

    .search-filter {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      justify-content: center;
    }

    #search {
      flex: 1;
      min-width: 250px;
      padding: 0.8rem;
      border: 2px solid #ddd;
      border-radius: 25px;
      font-size: 1rem;
      outline: none;
      transition: border-color 0.3s;
    }

    #search:focus {
      border-color: var(--primary);
    }

    .filter-buttons {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }

    .filter-btn {
      padding: 0.5rem 1rem;
      border: 2px solid var(--primary);
      background: white;
      color: var(--primary);
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.3s;
    }

    .filter-btn.active, .filter-btn:hover {
      background: var(--primary);
      color: white;
    }

    /* Recipe Grid */
    #recipe-container {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
      padding: 1rem;
      max-width: 1200px;
      margin: 0 auto;
    }

    .recipe-card {
      background: white;
      border-radius: 15px;
      overflow: hidden;
      box-shadow: var(--shadow);
      transition: transform 0.3s, box-shadow 0.3s;
      cursor: pointer;
    }

    .recipe-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }

    .recipe-image {
      width: 100%;
      height: 200px;
      object-fit: cover;
      border-bottom: 3px solid var(--primary);
    }

    .recipe-content {
      padding: 1rem;
    }

    .recipe-header {
      display: flex;
      justify-content: space-between;
      align-items: start;
      margin-bottom: 0.5rem;
    }

    .recipe-title {
      font-size: 1.2rem;
      font-weight: bold;
      color: var(--dark);
      margin-bottom: 0.5rem;
    }

    .recipe-meta {
      display: flex;
      gap: 1rem;
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      color: #666;
    }

    .badge {
      background: var(--secondary);
      color: white;
      padding: 0.2rem 0.5rem;
      border-radius: 10px;
      font-size: 0.8rem;
    }

    .rating {
      color: #ffc107;
    }

    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem;
      margin-top: 0.5rem;
    }

    .tag {
      background: #e0e0e0;
      padding: 0.2rem 0.5rem;
      border-radius: 10px;
      font-size: 0.8rem;
    }

    /* Feedback Modal */
    .modal {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      z-index: 1000;
      justify-content: center;
      align-items: center;
    }

    .modal-content {
      background: white;
      padding: 2rem;
      border-radius: 15px;
      width: 90%;
      max-width: 500px;
      max-height: 90vh;
      overflow-y: auto;
    }

    .close-btn {
      float: right;
      font-size: 1.5rem;
      cursor: pointer;
      color: #666;
    }

    .star-rating {
      display: flex;
      gap: 0.2rem;
      margin: 0.5rem 0;
    }

    .star {
      font-size: 1.5rem;
      color: #ddd;
      cursor: pointer;
      transition: color 0.2s;
    }

    .star:hover, .star.active {
      color: #ffc107;
    }

    .form-group {
      margin-bottom: 1rem;
    }

    .form-group label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: bold;
    }

    .form-group input, .form-group textarea, .form-group select {
      width: 100%;
      padding: 0.8rem;
      border: 2px solid #ddd;
      border-radius: 5px;
      font-size: 1rem;
    }

    .submit-btn {
      background: var(--primary);
      color: white;
      border: none;
      padding: 1rem 2rem;
      border-radius: 25px;
      cursor: pointer;
      font-size: 1rem;
      width: 100%;
      transition: background 0.3s;
    }

    .submit-btn:hover {
      background: #f4511e;
    }

    /* Stats Section */
    .stats {
      display: flex;
      justify-content: center;
      gap: 2rem;
      margin: 2rem 0;
      flex-wrap: wrap;
    }

    .stat-item {
      text-align: center;
      background: white;
      padding: 1rem;
      border-radius: 10px;
      box-shadow: var(--shadow);
      min-width: 150px;
    }

    .stat-number {
      font-size: 2rem;
      font-weight: bold;
      color: var(--primary);
    }

    /* Footer */
    footer {
      background: var(--dark);
      color: white;
      text-align: center;
      padding: 2rem 1rem;
      margin-top: 3rem;
    }

    .feedback-btn {
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 50%;
      width: 60px;
      height: 60px;
      font-size: 1.5rem;
      cursor: pointer;
      box-shadow: var(--shadow);
      z-index: 100;
      transition: transform 0.3s;
    }

    .feedback-btn:hover {
      transform: scale(1.1);
    }

    /* Success Message */
    .success-message {
      background: #4caf50;
      color: white;
      padding: 1rem;
      border-radius: 5px;
      margin: 1rem 0;
      display: none;
    }

    @media (max-width: 768px) {
      .header-content {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
      }

      #recipe-container {
        grid-template-columns: 1fr;
      }

      .search-filter {
        flex-direction: column;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="header-content">
      <div class="logo">
        <i class="fas fa-utensils"></i>
        <span>FlavorFinds</span>
      </div>
      <div class="tagline">Discover & Share Amazing Recipes</div>
    </div>
  </header>

  <div class="controls">
    <div class="search-filter">
      <input type="text" id="search" placeholder="Search recipes...">
      <div class="filter-buttons">
        <button class="filter-btn active" data-filter="all">All</button>
        <button class="filter-btn" data-filter="Breakfast">Breakfast</button>
        <button class="filter-btn" data-filter="Lunch">Lunch</button>
        <button class="filter-btn" data-filter="Dinner">Dinner</button>
        <button class="filter-btn" data-filter="Dessert">Dessert</button>
      </div>
    </div>
  </div>

  <div class="stats">
    <div class="stat-item">
      <div class="stat-number" id="total-recipes">0</div>
      <div>Total Recipes</div>
    </div>
    <div class="stat-item">
      <div class="stat-number" id="avg-rating">0.0</div>
      <div>Average Rating</div>
    </div>
    <div class="stat-item">
      <div class="stat-number" id="total-feedback">0</div>
      <div>Feedback Received</div>
    </div>
  </div>

  <div id="recipe-container">Loading recipes...</div>

  <!-- Feedback Button and Success Message -->
  <div class="success-message" id="successMessage">
    <i class="fas fa-check-circle"></i> Thank you for your feedback! We appreciate your input.
  </div>

  <button class="feedback-btn" onclick="openFeedbackModal()">
    <i class="fas fa-comment"></i>
  </button>

  <div id="feedbackModal" class="modal">
    <div class="modal-content">
      <span class="close-btn" onclick="closeFeedbackModal()">&times;</span>
      <h2>Share Your Feedback</h2>
      <form id="feedbackForm">
        <div class="form-group">
          <label for="name">Your Name:</label>
          <input type="text" id="name" name="name" required>
        </div>
        <div class="form-group">
          <label for="email">Email:</label>
          <input type="email" id="email" name="email" required>
        </div>
        <div class="form-group">
          <label for="recipeSelect">Recipe (Optional):</label>
          <select id="recipeSelect" name="recipe_id">
            <option value="">Select a recipe...</option>
          </select>
        </div>
        <div class="form-group">
          <label>Rating:</label>
          <div class="star-rating">
            <span class="star" data-rating="1">★</span>
            <span class="star" data-rating="2">★</span>
            <span class="star" data-rating="3">★</span>
            <span class="star" data-rating="4">★</span>
            <span class="star" data-rating="5">★</span>
          </div>
          <input type="hidden" id="rating" name="rating" required>
        </div>
        <div class="form-group">
          <label for="message">Your Message:</label>
          <textarea id="message" name="message" rows="4" placeholder="Tell us what you think about our recipes or suggest improvements..." required></textarea>
        </div>
        <button type="submit" class="submit-btn">
          <i class="fas fa-paper-plane"></i> Submit Feedback
        </button>
      </form>
    </div>
  </div>

  <footer>
    <p>&copy; 2024 FlavorFinds. All rights reserved.</p>
    <p>Share your culinary adventures with the world!</p>
    <button onclick="openFeedbackModal()" style="background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-top: 10px;">
      <i class="fas fa-comment-dots"></i> Give Feedback
    </button>
  </footer>

  <script>
    let recipes = [];
    let selectedRating = 0;

    // Load recipes and initialize the page
    document.addEventListener("DOMContentLoaded", async () => {
      await loadRecipes();
      await loadFeedbackStats();
      setupEventListeners();
    });

    async function loadRecipes() {
      try {
        const response = await fetch("/api/recipes");
        recipes = await response.json();
        displayRecipes(recipes);
        populateRecipeSelect();
        updateStats();
      } catch (error) {
        console.error("Error loading recipes:", error);
        document.getElementById("recipe-container").innerHTML = 
          "<p style='text-align: center; color: red;'>Error loading recipes. Please try again later.</p>";
      }
    }

    function displayRecipes(recipesToShow) {
      const container = document.getElementById("recipe-container");

      if (recipesToShow.length === 0) {
        container.innerHTML = "<p style='text-align: center;'>No recipes found matching your criteria.</p>";
        return;
      }

      container.innerHTML = recipesToShow.map(recipe => `
        <div class="recipe-card" onclick="showRecipeDetail(${recipe.id})">
          <img src="${recipe.img}" alt="${recipe.name}" class="recipe-image">
          <div class="recipe-content">
            <div class="recipe-header">
              <h3 class="recipe-title">${recipe.name}</h3>
              <span class="badge">${recipe.difficulty}</span>
            </div>
            <p>${recipe.desc}</p>
            <div class="recipe-meta">
              <span><i class="fas fa-clock"></i> ${recipe.time}</span>
              <span class="rating">⭐ ${recipe.rating}</span>
              <span><i class="fas fa-fire"></i> ${recipe.calories || 'N/A'} cal</span>
            </div>
            <div class="tags">
              ${recipe.tags.map(tag => `<span class="tag">#${tag}</span>`).join('')}
            </div>
            <button onclick="event.stopPropagation(); openFeedbackModal(${recipe.id})" 
                    style="background: var(--primary); color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; margin-top: 10px; width: 100%;">
              <i class="fas fa-star"></i> Rate this Recipe
            </button>
          </div>
        </div>
      `).join('');
    }

    function populateRecipeSelect() {
      const select = document.getElementById("recipeSelect");
      select.innerHTML = '<option value="">Select a recipe...</option>' +
        recipes.map(recipe => `<option value="${recipe.id}">${recipe.name}</option>`).join('');
    }

    function setupEventListeners() {
      // Search functionality
      document.getElementById("search").addEventListener("input", (e) => {
        filterRecipes();
      });

      // Filter buttons
      document.querySelectorAll(".filter-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
          document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
          e.target.classList.add("active");
          filterRecipes();
        });
      });

      // Star rating
      document.querySelectorAll(".star").forEach(star => {
        star.addEventListener("click", (e) => {
          selectedRating = parseInt(e.target.getAttribute("data-rating"));
          document.getElementById("rating").value = selectedRating;

          document.querySelectorAll(".star").forEach(s => {
            s.classList.toggle("active", parseInt(s.getAttribute("data-rating")) <= selectedRating);
          });
        });
      });

      // Feedback form submission
      document.getElementById("feedbackForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        await submitFeedback();
      });
    }

    function filterRecipes() {
      const searchTerm = document.getElementById("search").value.toLowerCase();
      const activeFilter = document.querySelector(".filter-btn.active").getAttribute("data-filter");

      const filtered = recipes.filter(recipe => {
        const matchesSearch = recipe.name.toLowerCase().includes(searchTerm) || 
                             recipe.desc.toLowerCase().includes(searchTerm) ||
                             recipe.tags.some(tag => tag.toLowerCase().includes(searchTerm));
        const matchesFilter = activeFilter === "all" || recipe.type === activeFilter;
        return matchesSearch && matchesFilter;
      });

      displayRecipes(filtered);
    }

    function updateStats() {
      document.getElementById("total-recipes").textContent = recipes.length;

      const avgRating = recipes.reduce((sum, recipe) => sum + recipe.rating, 0) / recipes.length;
      document.getElementById("avg-rating").textContent = avgRating.toFixed(1);
    }

    async function loadFeedbackStats() {
      try {
        const response = await fetch("/api/feedback/stats");
        const stats = await response.json();
        document.getElementById("total-feedback").textContent = stats.total_feedback;
      } catch (error) {
        console.error("Error loading feedback stats:", error);
      }
    }

    function openFeedbackModal(recipeId = null) {
      document.getElementById("feedbackModal").style.display = "flex";
      selectedRating = 0;
      document.getElementById("rating").value = "";
      document.querySelectorAll(".star").forEach(s => s.classList.remove("active"));
      document.getElementById("feedbackForm").reset();

      if (recipeId) {
        document.getElementById("recipeSelect").value = recipeId;
      }
    }

    function closeFeedbackModal() {
      document.getElementById("feedbackModal").style.display = "none";
    }

    function showSuccessMessage() {
      const successMsg = document.getElementById("successMessage");
      successMsg.style.display = "block";
      setTimeout(() => {
        successMsg.style.display = "none";
      }, 5000);
    }

    async function submitFeedback() {
      const formData = new FormData(document.getElementById("feedbackForm"));
      const feedbackData = {
        name: formData.get('name'),
        email: formData.get('email'),
        rating: parseInt(formData.get('rating')),
        message: formData.get('message'),
        recipe_id: formData.get('recipe_id') ? parseInt(formData.get('recipe_id')) : null
      };

      // Validation
      if (!feedbackData.name || !feedbackData.email || !feedbackData.rating || !feedbackData.message) {
        alert("Please fill in all required fields.");
        return;
      }

      try {
        const response = await fetch("/api/feedback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(feedbackData)
        });

        if (response.ok) {
          showSuccessMessage();
          closeFeedbackModal();
          await loadFeedbackStats();
        } else {
          alert("Error submitting feedback. Please try again.");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("Error submitting feedback. Please try again.");
      }
    }

    function showRecipeDetail(recipeId) {
      alert(`Recipe Details:\n\nName: ${recipes.find(r => r.id === recipeId)?.name}\n\nThis would show detailed recipe view with ingredients and steps in a complete application.`);
    }

    // Close modal when clicking outside
    window.onclick = function(event) {
      const modal = document.getElementById("feedbackModal");
      if (event.target === modal) {
        closeFeedbackModal();
      }
    }
  </script>
</body>
</html>
"""

# ---------- Feedback Storage ----------
FEEDBACK_FILE = "data/feedback.json"


def load_feedback():
    try:
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, 'r') as f:
                data = json.load(f)
                return [Feedback(**item) for item in data]
    except Exception as e:
        print(f"Error loading feedback: {e}")
    return []


def save_feedback(feedback_list):
    try:
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump([f.dict() for f in feedback_list], f, indent=2)
    except Exception as e:
        print(f"Error saving feedback: {e}")


# ---------- Routes ----------
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return HTML_PAGE


@app.get("/api/recipes", response_model=List[Recipe])
async def get_recipes():
    return recipes_db


@app.get("/api/recipes/{recipe_id}", response_model=Recipe)
async def get_recipe(recipe_id: int):
    for r in recipes_db:
        if r.id == recipe_id:
            return r
    raise HTTPException(status_code=404, detail="Recipe not found")


@app.post("/api/feedback")
async def submit_feedback(feedback: Feedback):
    feedback_list = load_feedback()

    # Update timestamp
    feedback.timestamp = datetime.now().isoformat()

    feedback_list.append(feedback)
    save_feedback(feedback_list)

    return {"message": "Feedback submitted successfully"}


@app.get("/api/feedback/stats")
async def get_feedback_stats():
    feedback_list = load_feedback()
    total_feedback = len(feedback_list)
    average_rating = sum(f.rating for f in feedback_list) / total_feedback if total_feedback > 0 else 0

    return {
        "total_feedback": total_feedback,
        "average_rating": round(average_rating, 1)
    }


@app.get("/api/feedback")
async def get_all_feedback():
    return load_feedback()


# ---------- Port Check Function ----------
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False


# ---------- Run with Port Checking ----------
if __name__ == "__main__":
    # Try different ports if 8000 is busy
    ports_to_try = [8000, 8001, 8002, 8003, 8004, 8080, 8081]

    for port in ports_to_try:
        if is_port_available(port):
            print(f"Starting server on port {port}...")
            uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
            break
        else:
            print(f"Port {port} is busy, trying next port...")
    else:
        print("All ports are busy! Please close other applications and try again.")
