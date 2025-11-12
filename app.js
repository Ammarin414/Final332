// 
// =================================================================
// !! สำคัญ !!
// วาง Public DNS ของ EC2 (ที่ได้จาก Step 2c) ที่นี่
// **ต้องมี http:// และ :5000 ด้วย**
// =================================================================
//
const apiUrl = "http://YOUR_EC2_PUBLIC_DNS_GOES_HERE:5000"; // เช่น http://ec2-xx-xx-xx.compute-1.amazonaws.com:5000
//
// =================================================================
//

const todoForm = document.getElementById('todo-form');
const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');
const loadingIndicator = document.getElementById('loading-indicator');
const errorMessage = document.getElementById('error-message');

let todos = []; // Local cache of todos

// --- Utility Functions ---

function showLoading(isLoading) {
    loadingIndicator.style.display = isLoading ? 'block' : 'none';
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = message ? 'block' : 'none';
}

function renderTodos() {
    todoList.innerHTML = ''; // Clear existing list
    if (todos.length === 0) {
        todoList.innerHTML = '<li>No tasks yet. Add one!</li>';
        return;
    }
    
    // Sort todos: incomplete first, then complete
    todos.sort((a, b) => a.completed - b.completed);

    todos.forEach(todo => {
        const li = document.createElement('li');
        li.className = todo.completed ? 'completed' : '';
        li.dataset.id = todo.id;

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = todo.completed;
        checkbox.addEventListener('change', () => toggleTodoComplete(todo.id, !todo.completed));
        
        const text = document.createElement('span');
        text.textContent = todo.text;
        text.style.flexGrow = '1'; // Make text span fill available space
        text.addEventListener('click', () => toggleTodoComplete(todo.id, !todo.completed)); // Allow clicking text

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.textContent = 'X';
        deleteBtn.addEventListener('click', () => deleteTodo(todo.id));

        li.appendChild(checkbox);
        li.appendChild(text);
        li.appendChild(deleteBtn);
        todoList.appendChild(li);
    });
}

// --- API Call Functions ---

// GET /todos
async function fetchTodos() {
    showLoading(true);
    showError('');
    try {
        const response = await fetch(`${apiUrl}/todos`, { method: 'GET' });
        if (!response.ok) {
            throw new Error(`Failed to fetch todos: ${response.statusText}`);
        }
        todos = await response.json();
        renderTodos();
    } catch (error) {
        console.error(error);
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// POST /todos
async function addTodo(event) {
    event.preventDefault();
    const text = todoInput.value.trim();
    if (text === '') return;

    showLoading(true);
    showError('');
    
    try {
        const response = await fetch(`${apiUrl}/todos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to add todo: ${response.statusText}`);
        }
        
        const newTodo = await response.json();
        todos.push(newTodo);
        todoInput.value = ''; // Clear input
        renderTodos();
    } catch (error) {
        console.error(error);
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// PUT /todos (for updates)
async function toggleTodoComplete(id, isCompleted) {
    showError('');
    try {
        const response = await fetch(`${apiUrl}/todos`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id, completed: isCompleted })
        });

        if (!response.ok) {
            throw new Error(`Failed to update todo: ${response.statusText}`);
        }
        
        // Update local cache
        const updatedTodo = await response.json();
        const todoIndex = todos.findIndex(t => t.id === id);
        if (todoIndex > -1) {
            todos[todoIndex] = updatedTodo;
        }
        renderTodos();
    } catch (error) {
        console.error(error);
        showError(error.message);
    }
}

// DELETE /todos
async function deleteTodo(id) {
    showError('');
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }

    try {
        const response = await fetch(`${apiUrl}/todos`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id })
        });

        if (!response.ok) {
            throw new Error(`Failed to delete todo: ${response.statusText}`);
        }

        // Remove from local cache
        todos = todos.filter(t => t.id !== id);
        renderTodos();
    } catch (error) {
        console.error(error);
        showError(error.message);
    }
}

// --- Initial Load ---

// Add event listener to the form
todoForm.addEventListener('submit', addTodo);

// Initial fetch of todos when the page loads
fetchTodos();
