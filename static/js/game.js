document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const joinForm = document.querySelector('.join-form');
    const gameArea = document.querySelector('.game-area');
    const playerNameInput = document.getElementById('playerName');
    const joinBtn = document.getElementById('joinBtn');
    const playersList = document.getElementById('playersList');
    const connectionStatus = document.getElementById('connectionStatus');
    const gameStatus = document.getElementById('gameStatus');
    const spaceship = document.getElementById('spaceship');
    const spaceshipContainer = document.getElementById('spaceshipContainer');
    
    // Control buttons
    const upBtn = document.getElementById('upBtn');
    const downBtn = document.getElementById('downBtn');
    const leftBtn = document.getElementById('leftBtn');
    const rightBtn = document.getElementById('rightBtn');
    
    // Game variables
    let socket = null;
    let playerName = '';
    let playerId = '';
    let isConnected = false;
    let gameState = {
        shipX: 50, // position as percentage of container
        shipY: 50
    };
    let gameObjects = []; // Store all game objects for rendering
    
    // Track pressed keys locally
    const pressedKeys = {
        up: false,
        down: false,
        left: false,
        right: false
    };
    
    // Initialize the game connection
    function initConnection() {
        socket = io();
        
        // Connection events
        socket.on('connect', () => {
            isConnected = true;
            connectionStatus.textContent = 'Connected to game server!';
            connectionStatus.className = 'connected';
            playerId = socket.id;
        });
        
        socket.on('disconnect', () => {
            isConnected = false;
            connectionStatus.textContent = 'Disconnected from server. Trying to reconnect...';
            connectionStatus.className = 'disconnected';
            
            // Reset key states on disconnect
            Object.keys(pressedKeys).forEach(key => pressedKeys[key] = false);
        });
        
        // Game events
        socket.on('player_list', (players) => {
            updatePlayersList(players);
        });
        
        socket.on('player_joined', (player) => {
            addPlayerToList(player);
            connectionStatus.textContent = `${player.name} has joined the game!`;
            setTimeout(() => {
                if (isConnected) connectionStatus.textContent = 'Connected to game server!';
            }, 3000);
        });
        
        socket.on('player_left', (player) => {
            removePlayerFromList(player);
            connectionStatus.textContent = `${player.name} has left the game!`;
            setTimeout(() => {
                if (isConnected) connectionStatus.textContent = 'Connected to game server!';
            }, 3000);
        });
        
        socket.on('player_updated', (player) => {
            updatePlayerInList(player);
        });
        
        // Game state update event
        socket.on('game_state_update', (newState) => {
            updateGameState(newState);
        });
        
        socket.on('player_action', (action) => {
            gameStatus.textContent = `${action.player} moved the ship ${action.direction}!`;
            setTimeout(() => {
                gameStatus.textContent = 'Game in progress...';
            }, 2000);
        });
    }
    
    // Update the displayed list of players
    function updatePlayersList(players) {
        playersList.innerHTML = '';
        players.forEach(player => {
            addPlayerToList(player);
        });
    }
    
    function addPlayerToList(player) {
        const playerElement = document.createElement('li');
        playerElement.id = `player-${player.id}`;
        playerElement.textContent = player.name;
        if (player.id === playerId) {
            playerElement.classList.add('current-player');
            playerElement.textContent += ' (You)';
        }
        playersList.appendChild(playerElement);
    }
    
    function removePlayerFromList(player) {
        const playerElement = document.getElementById(`player-${player.id}`);
        if (playerElement) {
            playerElement.remove();
        }
    }
    
    function updatePlayerInList(player) {
        const playerElement = document.getElementById(`player-${player.id}`);
        if (playerElement) {
            playerElement.textContent = player.name;
            if (player.id === playerId) {
                playerElement.textContent += ' (You)';
            }
        }
    }
    
    // Update game state and render all game objects
    function updateGameState(newState) {
        gameState = newState;
        
        // Update spaceship
        if (spaceship) {
            spaceship.style.left = `${gameState.shipX}%`;
            spaceship.style.top = `${gameState.shipY}%`;
            
            // Apply image properties if they exist
            if (gameState.image) {
                spaceship.style.width = `${gameState.image.width}px`;
                spaceship.style.height = `${gameState.image.height}px`;
                spaceship.style.backgroundImage = `url(${gameState.image.url})`;
                spaceship.style.backgroundSize = 'contain';
                spaceship.style.backgroundRepeat = 'no-repeat';
                spaceship.style.backgroundPosition = 'center';
                spaceship.style.transform = `translate(-50%, -50%) rotate(${gameState.image.angle}rad)`;
                spaceship.style.opacity = gameState.image.opacity;
            }
        }
        
        // If we have game objects with images, render them
        if (gameState.gameObjects) {
            renderGameObjects(gameState.gameObjects);
        }
    }
    
    // Render all game objects
    function renderGameObjects(objects) {
        // Clear existing objects
        const existingObjects = spaceshipContainer.querySelectorAll('.game-object');
        existingObjects.forEach(obj => {
            if (obj.id !== 'spaceship') { // Don't remove the main spaceship
                obj.remove();
            }
        });
        
        // Create or update game objects
        objects.forEach(obj => {
            // Skip if no image to display
            if (!obj.image) return;
            
            let element = document.getElementById(`game-object-${obj.id}`);
            
            // Create if doesn't exist
            if (!element) {
                element = document.createElement('div');
                element.id = `game-object-${obj.id}`;
                element.classList.add('game-object');
                spaceshipContainer.appendChild(element);
            }
            
            // Set position and size
            element.style.left = `${obj.x}%`;
            element.style.top = `${obj.y}%`;
            element.style.width = `${obj.image.width}px`;
            element.style.height = `${obj.image.height}px`;
            
            // Set image and transformation
            element.style.backgroundImage = `url(${obj.image.url})`;
            element.style.backgroundSize = 'contain';
            element.style.backgroundRepeat = 'no-repeat';
            element.style.backgroundPosition = 'center';
            element.style.transform = `translate(-50%, -50%) rotate(${obj.image.angle}rad)`;
            element.style.opacity = obj.image.opacity;
            
            // Set visibility based on active state
            element.style.display = obj.active ? 'block' : 'none';
            
            // Debug: show colliders if present
            if (obj.colliders && window.debugMode) {
                renderCollider(element, obj.colliders);
            }
        });
    }
    
    // Debug function to visualize colliders
    function renderCollider(element, colliders) {
        // Clear existing collider visualizations
        element.querySelectorAll('.collider-debug').forEach(el => el.remove());
        
        // Create a visualization for each collider
        if (Array.isArray(colliders)) {
            colliders.forEach((collider, index) => {
                const colliderEl = document.createElement('div');
                colliderEl.classList.add('collider-debug');
                colliderEl.dataset.index = index;
                element.appendChild(colliderEl);
                
                colliderEl.style.width = `${collider.width}px`;
                colliderEl.style.height = `${collider.height}px`;
                colliderEl.style.transform = `translate(${collider.offsetX}px, ${collider.offsetY}px) rotate(${collider.angle}rad)`;
            });
        }
    }
    
    // Send key state change to server
    function sendKeyState(key, isPressed) {
        if (isConnected && gameArea.classList.contains('hidden') === false) {
            if (isPressed) {
                socket.emit('key_down', { key });
            } else {
                socket.emit('key_up', { key });
            }
        }
    }
    
    // Handle key press and release for continuous movement
    function handleKeyDown(key) {
        if (!pressedKeys[key]) {
            pressedKeys[key] = true;
            sendKeyState(key, true);
            
            // Visual feedback for button
            const btnMap = { up: upBtn, down: downBtn, left: leftBtn, right: rightBtn };
            if (btnMap[key]) {
                btnMap[key].classList.add('active');
            }
        }
    }
    
    function handleKeyUp(key) {
        if (pressedKeys[key]) {
            pressedKeys[key] = false;
            sendKeyState(key, false);
            
            // Visual feedback for button
            const btnMap = { up: upBtn, down: downBtn, left: leftBtn, right: rightBtn };
            if (btnMap[key]) {
                btnMap[key].classList.remove('active');
            }
        }
    }
    
    // Setup control buttons
    upBtn.addEventListener('mousedown', () => handleKeyDown('up'));
    upBtn.addEventListener('mouseup', () => handleKeyUp('up'));
    upBtn.addEventListener('mouseleave', () => handleKeyUp('up'));
    
    downBtn.addEventListener('mousedown', () => handleKeyDown('down'));
    downBtn.addEventListener('mouseup', () => handleKeyUp('down'));
    downBtn.addEventListener('mouseleave', () => handleKeyUp('down'));
    
    leftBtn.addEventListener('mousedown', () => handleKeyDown('left'));
    leftBtn.addEventListener('mouseup', () => handleKeyUp('left'));
    leftBtn.addEventListener('mouseleave', () => handleKeyUp('left'));
    
    rightBtn.addEventListener('mousedown', () => handleKeyDown('right'));
    rightBtn.addEventListener('mouseup', () => handleKeyUp('right'));
    rightBtn.addEventListener('mouseleave', () => handleKeyUp('right'));
    
    // For touch devices
    upBtn.addEventListener('touchstart', (e) => { e.preventDefault(); handleKeyDown('up'); });
    upBtn.addEventListener('touchend', (e) => { e.preventDefault(); handleKeyUp('up'); });
    
    downBtn.addEventListener('touchstart', (e) => { e.preventDefault(); handleKeyDown('down'); });
    downBtn.addEventListener('touchend', (e) => { e.preventDefault(); handleKeyUp('down'); });
    
    leftBtn.addEventListener('touchstart', (e) => { e.preventDefault(); handleKeyDown('left'); });
    leftBtn.addEventListener('touchend', (e) => { e.preventDefault(); handleKeyUp('left'); });
    
    rightBtn.addEventListener('touchstart', (e) => { e.preventDefault(); handleKeyDown('right'); });
    rightBtn.addEventListener('touchend', (e) => { e.preventDefault(); handleKeyUp('right'); });
    
    // Add keyboard controls
    document.addEventListener('keydown', (e) => {
        if (!isConnected || gameArea.classList.contains('hidden')) return;
        
        switch (e.key) {
            case 'ArrowUp':
                handleKeyDown('up');
                break;
            case 'ArrowDown':
                handleKeyDown('down');
                break;
            case 'ArrowLeft':
                handleKeyDown('left');
                break;
            case 'ArrowRight':
                handleKeyDown('right');
                break;
        }
    });
    
    document.addEventListener('keyup', (e) => {
        if (!isConnected) return;
        
        switch (e.key) {
            case 'ArrowUp':
                handleKeyUp('up');
                break;
            case 'ArrowDown':
                handleKeyUp('down');
                break;
            case 'ArrowLeft':
                handleKeyUp('left');
                break;
            case 'ArrowRight':
                handleKeyUp('right');
                break;
        }
    });
    
    // Handle leaving the window or tab
    window.addEventListener('blur', () => {
        // Release all keys when window loses focus
        Object.keys(pressedKeys).forEach(key => {
            if (pressedKeys[key]) {
                handleKeyUp(key);
            }
        });
    });
    
    // Join button event handler
    joinBtn.addEventListener('click', () => {
        playerName = playerNameInput.value.trim() || `Player ${Math.floor(Math.random() * 1000)}`;
        
        // Initialize connection if not already done
        if (!socket) {
            initConnection();
        }
        
        // Send player name to server
        if (isConnected) {
            socket.emit('set_name', { name: playerName });
            joinForm.classList.add('hidden');
            gameArea.classList.remove('hidden');
            gameStatus.textContent = 'Game in progress...';
            
            // Request initial game state
            socket.emit('request_game_state');
        } else {
            connectionStatus.textContent = 'Waiting for connection to server...';
            // Try again in a second
            setTimeout(() => {
                if (isConnected) {
                    socket.emit('set_name', { name: playerName });
                    joinForm.classList.add('hidden');
                    gameArea.classList.remove('hidden');
                    gameStatus.textContent = 'Game in progress...';
                    
                    // Request initial game state
                    socket.emit('request_game_state');
                } else {
                    connectionStatus.textContent = 'Could not connect to server. Please try again.';
                }
            }, 1000);
        }
    });
    
    // Allow pressing Enter to join
    playerNameInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            joinBtn.click();
        }
    });
});
