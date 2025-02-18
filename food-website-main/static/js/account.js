const categories = document.getElementById("categories");
const food = document.getElementById("food");


const MEAL_SEARCH_URL = "https://www.themealdb.com/api/json/v1/1/lookup.php?i=";
const INGREDIANT_IMAGE_URL = "https://www.themealdb.com/images/ingredients/";
const INGREDIANT_SEARCH_URL = 'https://www.themealdb.com/api/json/v1/1/filter.php?i=';


function get_liked_meal(url, id) {
    categories.innerHTML = ``;

    fetch(url + id).then(res => res.json()).then(data => {
        // console.log(data);

        for (let i = 0; i < data.meals.length; i++) {
            const category = document.createElement('div');
            category.classList.add('category');
            category.innerHTML = `
            <div id="${data.meals[i].idMeal}">
                <h1>${data.meals[i].strMeal}</h1>
                <img src="${data.meals[i].strMealThumb}">
            </div>
            `
            categories.appendChild(category);
            let id = data.meals[i].idMeal;
            document.getElementById(id).addEventListener('click', () => {
                // console.log(id);
                open_food(MEAL_SEARCH_URL, id);
            })

        }

    })
}


function open_food(url, id) {
    fetch(url + id).then(res => res.json()).then(data => {
        // console.log(data);

        // Filter list 
        const meal = data.meals[0];
        const ingredients = [];
        const measures = [];
        const image_url = [];

        for (let i = 1; i <= 20; i++) {
            const thisIngredient = meal[`strIngredient${i}`];
            const thisMeasure = meal[`strMeasure${i}`];
            if (thisIngredient) {
                ingredients.push(thisIngredient);
                measures.push(thisMeasure);
            }
        }

        const filteredIngredients = ingredients.filter(Boolean);
        const filteredMeasures = measures.filter(Boolean);

        categories.innerHTML = ``;
        food.innerHTML = ``;
        food.innerHTML = `
        <div class="title">
            <h1>${data.meals[0].strMeal}</h1>
        </div>
        <div class="food-container" id="food-container">
        <div class="data">
            <img src="${data.meals[0].strMealThumb}">
            <span class='area' id='${data.meals[0].strArea}' style='cursor: pointer;'>${data.meals[0].strArea}</span>
            <span>${data.meals[0].strCategory}</span>
            <span class='like' id='${data.meals[0].idMeal}' style='color: white; cursor: pointer;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="24" id="heart"><path id='heartFill' fill="#f05542" d="M5.301 3.002c-.889-.047-1.759.247-2.404.893-1.29 1.292-1.175 3.49.26 4.926l.515.515L8.332 14l4.659-4.664.515-.515c1.435-1.437 1.55-3.634.26-4.926-1.29-1.292-3.483-1.175-4.918.262l-.516.517-.517-.517C7.098 3.438 6.19 3.049 5.3 3.002z"></path></svg>
            </span>
        </div>
        <div class="ingredients" id="ingredients">
        </div>
        </div>
        `
        // Liked Meals

        // Unlike 
        let liked_meal_id = data.meals[0].idMeal;
        document.getElementById(liked_meal_id).addEventListener('click', () => {
            // addLikedMeal(liked_meal_id);
            removeLikedMeal(liked_meal_id);
            document.getElementById('heartFill').style.fill = '#FFFFFF';
        })

        // Area 
        let area = data.meals[0].strArea;
        document.getElementById(area).addEventListener('click', () => {
            // console.log(area);
            // open_category(AREA_FILER_URL, area);
            alert();
        })

        // Ingredients 
        for (let i = 0; i <= filteredIngredients.length - 1; i++) {
            // console.log(filteredIngredients[i]);
            const url = INGREDIANT_IMAGE_URL + filteredIngredients[i] + '.png';
            image_url.push(url);
            // console.log(image_url[i]);

            const ingrediant = document.createElement('div');
            ingrediant.classList.add('ingredient');
            ingrediant.innerHTML = `
                <div id="${filteredIngredients[i]}" >
                    <img src="${image_url[i]}" style="max-width: 10vw;" ">
                    <span class='ingredient_hover'>${filteredIngredients[i]}</span>
                    <span>${filteredMeasures[i]}</span>
                </div>
            `;

            document.getElementById("ingredients").appendChild(ingrediant);
            let id = filteredIngredients[i];
            document.getElementById(id).addEventListener('click', () => {
                // console.log(id);
                // open_category(INGREDIANT_SEARCH_URL, id);
                alert()
            });
        }
        // Instructions
        const instructions = document.createElement('div');
        instructions.classList.add('instructions');
        const youtube_url = data.meals[0].strYoutube;
        const videoId = youtube_url.split("=")[1];
        instructions.innerHTML = `
            <div class="instruction">
                <h1>Instructions</h1>
                <span>${data.meals[0].strInstructions}</span>
            </div>
            <div class="youtube">
                <iframe width="560" height="315" src="https://www.youtube.com/embed/${videoId}"
                    title="YouTube video player" frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowfullscreen>
                </iframe>
            </div>`;
        food.appendChild(instructions);
        // console.log(data.meals[0]);
    })
}


function getLikedMeals() {
    fetch('/get_liked_meals').then(res => res.json()).then(data => {
        // console.log(data)
        // console.log(data.likedMeals.length)
        let i = 0
        for (i = 0; i < data.likedMeals.length; i++) {
            // console.log(data.likedMeals[i])
            get_liked_meal(MEAL_SEARCH_URL, data.likedMeals[i])
        }
    })
}


function removeLikedMeal(idMeal) {
    // Send a POST request to add a meal
    fetch('/remove_liked_meals', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idMeal: idMeal }),
    })
        .then(response => response.json())
        .then(result => {
            console.log(result);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

getLikedMeals()