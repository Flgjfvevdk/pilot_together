document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const joinForm = document.querySelector('.join-form');
    const gameArea = document.querySelector('.game-area');
    const playerNameInput = document.getElementById('playerName');
    const joinBtn = document.getElementById('joinBtn');
    const playersList = document.getElementById('playersList');
    const connectionStatus = document.getElementById('connectionStatus');
    const gameStatus = document.getElementById('gameStatus');
    const spaceshipContainer = document.getElementById('spaceshipContainer');
    
    // La référence au vaisseau - maintenir une seule référence
    const spaceship = document.getElementById('spaceship');
    if (spaceship) {
        spaceship.classList.add('game-object');
    }
    
    // Control buttons
    const upBtn = document.getElementById('upBtn');
    const downBtn = document.getElementById('downBtn');
    const leftBtn = document.getElementById('leftBtn');
    const rightBtn = document.getElementById('rightBtn');
    
    const coolBtn = document.getElementById('coolBtn');
    
    // Shield button
    const shieldBtn = document.getElementById('shieldBtn');
    
    // Repair buttons & état
    const repairBtns = Array.from({length:10}, (_,i) => document.getElementById(`repairBtn${i}`));
    let activeRepair = null;

    function pickNewRepair() {
        if (activeRepair !== null) repairBtns[activeRepair].classList.remove('active');
        activeRepair = Math.floor(Math.random() * repairBtns.length);
        repairBtns[activeRepair].classList.add('active');
    }

    // Weapon selection buttons
    const weaponBtns = [
        document.getElementById('weapon1Btn'),
        document.getElementById('weapon2Btn'),
        document.getElementById('weapon3Btn'),
        document.getElementById('weapon4Btn')
    ];

    let currentWeapon = 1; // Default weapon selection

    // setup listeners
    repairBtns.forEach((btn, idx) => {
        btn.addEventListener('click', () => {
            if (idx === activeRepair) {
                socket.emit('repair');    // demande de réparation
                pickNewRepair();
            }
        });
        // touch support
        btn.addEventListener('touchstart', e => { e.preventDefault(); });
        btn.addEventListener('touchend', e => {
            e.preventDefault();
            // clear all highlights
            repairBtns.forEach(b => b.classList.remove('active'));
            // if correct button, trigger and pick new, else do nothing
            if (idx === activeRepair) {
                socket.emit('repair');
                pickNewRepair();
            }
            // highlight the (new) active button
            repairBtns[activeRepair].classList.add('active');
        });
        btn.addEventListener('touchcancel', e => {
            e.preventDefault();
            repairBtns.forEach(b => b.classList.remove('active'));
            repairBtns[activeRepair].classList.add('active');
        });
    });

    // démarre l’activation
    pickNewRepair();

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
        right: false,
        cool: false,
        shield: false,
        weapon: 1 // Default weapon selection
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
        
        // Événement de mise à jour de santé du vaisseau
        socket.on('spaceship_health_update', (data) => {
            if (data.health) {
                updateShipHealthBar(data.health);
            }
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
        
        // Create a sorted copy of the game objects
        let sortedObjects = [...gameState.gameObjects];
        
        // Sort objects by z-index for proper rendering order (lower z-index first)
        sortedObjects.sort((a, b) => (a.z_index || 0) - (b.z_index || 0));
        
        // Render all game objects with a unified approach
        renderGameObjects(sortedObjects);
        
        // Update spaceship health bar if the spaceship exists
        const shipObject = sortedObjects.find(obj => obj.id === 'spaceship');
        if (shipObject && shipObject.health) {
            updateShipHealthBar(shipObject.health);
            if (shipObject.temperature !== undefined) {
                updateTemperatureBar(shipObject.temperature, shipObject.maxTemperature);
            }
        }
    }
    
    // Créer et initialiser la barre de santé du vaisseau dans l'interface
    function initializeShipHealthBar() {
        // Ne créer que si elle n'existe pas déjà
        if (document.querySelector('.ship-health-container')) {
            return;
        }
        
        // Créer la structure de la barre de santé
        const healthContainer = document.createElement('div');
        healthContainer.className = 'ship-health-container';
        
        const healthBar = document.createElement('div');
        healthBar.className = 'ship-health-bar';
        
        const healthText = document.createElement('div');
        healthText.className = 'ship-health-text';
        healthText.textContent = 'Vaisseau: 100%';
        
        healthContainer.appendChild(healthBar);
        healthContainer.appendChild(healthText);
        
        // Insérer avant la zone de jeu
        const gameBoard = document.querySelector('.game-board');
        if (gameBoard) {
            gameBoard.insertBefore(healthContainer, gameBoard.firstChild);
            // temperature bar
            const tempContainer = document.createElement('div');
            tempContainer.className = 'ship-temp-container';
            const tempBar = document.createElement('div');
            tempBar.className = 'ship-temp-bar';
            const tempText = document.createElement('div');
            tempText.className = 'ship-temp-text';
            tempText.textContent = 'Température: 0%';
            tempContainer.appendChild(tempBar);
            tempContainer.appendChild(tempText);
            gameBoard.insertBefore(tempContainer, healthContainer.nextSibling);
        }
    }
    
    // Mise à jour de la barre de santé du vaisseau
    function updateShipHealthBar(health) {
        // S'assurer que la barre existe
        if (!document.querySelector('.ship-health-container')) {
            initializeShipHealthBar();
        }
        
        const healthBar = document.querySelector('.ship-health-bar');
        const healthText = document.querySelector('.ship-health-text');
        
        if (healthBar && healthText) {
            const healthPercent = (health.current / health.max) * 100;
            healthBar.style.width = `${healthPercent}%`;
            healthText.textContent = `Vaisseau: ${Math.round(healthPercent)}%`;
            
            // Mise à jour des classes en fonction du niveau de santé
            healthBar.classList.remove('warning', 'danger');
            if (healthPercent <= 25) {
                healthBar.classList.add('danger');
            } else if (healthPercent <= 50) {
                healthBar.classList.add('warning');
            }
        }
    }
    
    // Met à jour la barre de température du vaisseau
    function updateTemperatureBar(temp, maxTemp) {
        if (!document.querySelector('.ship-temp-container')) return;
        const tempBar = document.querySelector('.ship-temp-bar');
        const tempText = document.querySelector('.ship-temp-text');
        const pct = (temp / maxTemp) * 100;
        tempBar.style.width = `${pct}%`;
        tempText.textContent = `Température: ${Math.round(pct)}%`;
        tempBar.classList.remove('overheat', 'warning','danger');
        if (pct >= 100) tempBar.classList.add('overheat');
        else if (pct >= 75) tempBar.classList.add('danger');
        else if (pct >= 50) tempBar.classList.add('warning');
    }
    
    // Render all game objects
    function renderGameObjects(objects) {
        // Garder une référence aux objets existants pour éviter les recréations inutiles
        const existingElements = {};
        
        // Identifier les éléments existants (sauf le spaceship qui est déjà dans le DOM)
        const currentElements = spaceshipContainer.querySelectorAll('.game-object:not(#spaceship)');
        currentElements.forEach(el => {
            existingElements[el.id] = el;
        });
        
        // Ajouter spaceship à la liste des éléments existants si disponible
        if (spaceship) {
            existingElements['spaceship'] = spaceship;
        }
        
        // Liste des IDs d'objets rendus pour identifier ceux à supprimer plus tard
        const renderedIds = new Set();
        
        // Créer ou mettre à jour les objets de jeu
        objects.forEach(obj => {
            // Ignorer les objets sans données correctes
            if (!obj || !obj.hasOwnProperty('id')) return;
            
            let element;
            let elementId;
            
            // Cas spécial pour le vaisseau - utiliser la référence existante
            if (obj.id === 'spaceship') {
                elementId = 'spaceship';
                element = spaceship; 
                if (!element) {
                    console.error("Element with ID 'spaceship' not found in DOM");
                    return;
                }
                renderedIds.add(elementId);
                
            } else {
                // Traitement normal pour les autres objets
                elementId = `game-object-${obj.id}`;
                renderedIds.add(elementId);
                
                element = document.getElementById(elementId);
                if (!element) {
                    // Créer un nouvel élément
                    element = document.createElement('div');
                    element.id = elementId;
                    element.classList.add('game-object');
                    spaceshipContainer.appendChild(element);
                }
                
            }
            
            element.style.left = `${obj.x}%`;
            element.style.top = `${obj.y}%`;

            
            // Appliquer les propriétés d'image si présentes
            if (obj.image) {
                // Utiliser des tailles relatives quand possible
                const relativeWidth = obj.image.useRelativeSize ? obj.image.width : 8;
                const relativeHeight = obj.image.useRelativeSize ? obj.image.height : 8;
                
                element.style.width = `${relativeWidth}%`;
                element.style.height = `${relativeHeight}%`;
                element.style.backgroundImage = `url(${obj.image.url})`;
                element.style.backgroundSize = 'contain';
                element.style.backgroundRepeat = 'no-repeat';
                element.style.backgroundPosition = 'center';
                element.style.transform = `translate(-50%, -50%) rotate(${obj.image.angle || 0}rad)`;
                element.style.opacity = obj.image.opacity !== undefined ? obj.image.opacity : 1.0;
            }
            
            // Visibilité basée sur l'état actif
            element.style.display = obj.active !== false ? 'block' : 'none';
            
            // Debug : afficher les colliders si présents
            if (obj.colliders && window.debugMode) {
                renderCollider(element, obj.colliders);
            }
        });
        
        // Supprimer les éléments qui ne sont plus présents dans les données
        // Mais ne jamais supprimer l'élément spaceship original
        currentElements.forEach(el => {
            if (!renderedIds.has(el.id)) {
                el.remove();
            }
        });
    }
    
    // Fonction pour créer ou mettre à jour une barre de santé
    function updateOrCreateHealthBar(element, health) {
        if (!health) return;
        
        let healthBarContainer = element.querySelector('.health-bar-container');
        
        // Créer le conteneur de la barre de santé s'il n'existe pas
        if (!healthBarContainer) {
            healthBarContainer = document.createElement('div');
            healthBarContainer.className = 'health-bar-container';
            
            const healthBar = document.createElement('div');
            healthBar.className = 'health-bar';
            
            healthBarContainer.appendChild(healthBar);
            element.appendChild(healthBarContainer);
        }
        
        // Mettre à jour la barre de santé
        const healthBar = healthBarContainer.querySelector('.health-bar');
        const healthPercent = (health.current / health.max) * 100;
        healthBar.style.width = `${healthPercent}%`;
        
        // Mise à jour des classes en fonction du niveau de santé
        healthBar.classList.remove('warning', 'danger');
        if (healthPercent <= 25) {
            healthBar.classList.add('danger');
        } else if (healthPercent <= 50) {
            healthBar.classList.add('warning');
        }
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
            const btnMap = { 
                up: upBtn, 
                down: downBtn, 
                left: leftBtn, 
                right: rightBtn,
                cool: coolBtn,
                shield: shieldBtn
            };
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
            const btnMap = { 
                up: upBtn, 
                down: downBtn, 
                left: leftBtn, 
                right: rightBtn,
                cool: coolBtn,
                shield: shieldBtn
            };
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
    
    // Setup cool button
    coolBtn.addEventListener('mousedown', () => handleKeyDown('cool'));
    coolBtn.addEventListener('mouseup', () => handleKeyUp('cool'));
    coolBtn.addEventListener('mouseleave', () => handleKeyUp('cool'));
    coolBtn.addEventListener('touchstart', (e) => { e.preventDefault(); handleKeyDown('cool'); });
    coolBtn.addEventListener('touchend', (e) => { e.preventDefault(); handleKeyUp('cool'); });
    
    // Setup shield button
    shieldBtn.addEventListener('mousedown', () => handleKeyDown('shield'));
    shieldBtn.addEventListener('mouseup', () => handleKeyUp('shield'));
    shieldBtn.addEventListener('mouseleave', () => handleKeyUp('shield'));
    shieldBtn.addEventListener('touchstart', (e) => { e.preventDefault(); handleKeyDown('shield'); });
    shieldBtn.addEventListener('touchend', (e) => { e.preventDefault(); handleKeyUp('shield'); });
    shieldBtn.addEventListener('touchcancel', (e) => { e.preventDefault(); handleKeyUp('shield'); });

    // Setup weapon selection buttons
    weaponBtns.forEach((btn, index) => {
        const weaponNumber = index + 1;
        
        // Ajout de classes CSS spécifiques à chaque arme
        btn.classList.add(`weapon-${weaponNumber}`);
        
        btn.addEventListener('click', () => {
            // Deselect all buttons
            weaponBtns.forEach(b => b.classList.remove('active'));
            
            // Select the clicked button
            btn.classList.add('active');
            
            // Update weapon selection
            currentWeapon = weaponNumber;
            
            // Emit weapon selection change
            if (isConnected) {
                pressedKeys.weapon = currentWeapon;
                socket.emit('weapon_select', { weapon: currentWeapon });
            }
        });
    });

    // Add keyboard controls
    document.addEventListener('keydown', (e) => {
        if (!isConnected || gameArea.classList.contains('hidden')) return;
        
        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault(); // Prevent page scrolling
                handleKeyDown('up');
                break;
            case 'ArrowDown':
                e.preventDefault(); // Prevent page scrolling
                handleKeyDown('down');
                break;
            case 'ArrowLeft':
                e.preventDefault(); // Prevent page scrolling
                handleKeyDown('left');
                break;
            case 'ArrowRight':
                e.preventDefault(); // Prevent page scrolling
                handleKeyDown('right');
                break;
            case 's': 
                e.preventDefault();
                handleKeyDown('shield');
                break;
            case 'c':
                e.preventDefault();
                handleKeyDown('cool');
                break;
        }
    });
    
    document.addEventListener('keyup', (e) => {
        if (!isConnected) return;
        
        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault(); // Prevent page scrolling
                handleKeyUp('up');
                break;
            case 'ArrowDown':
                e.preventDefault(); // Prevent page scrolling
                handleKeyUp('down');
                break;
            case 'ArrowLeft':
                e.preventDefault(); // Prevent page scrolling
                handleKeyUp('left');
                break;
            case 'ArrowRight':
                e.preventDefault(); // Prevent page scrolling
                handleKeyUp('right');
                break;
            case 's': 
                e.preventDefault();
                handleKeyUp('shield');
                break;
            case 'c':
                e.preventDefault();
                handleKeyUp('cool');
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
            
            // Initialiser la barre de santé du vaisseau
            initializeShipHealthBar();
            
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
                    
                    // Initialiser la barre de santé du vaisseau
                    initializeShipHealthBar();
                    
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

    // Setup aim canvas
    function setupAimCanvas() {
        const canvas = document.getElementById('aimCanvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = (canvas.width / 2) - 10;
        
        let currentAngle = 0;
        let isFiring = false;
        let firingInterval = null;
        
        // Afficher les infos sur l'arme actuelle
        function updateWeaponInfo() {
            const weaponInfo = {
                1: { name: "Canon 1", color: "#2ecc71" },  // Vert
                2: { name: "Canon 2", color: "#e74c3c" },  // Rouge
                3: { name: "Canon 3", color: "#3498db" },  // Bleu
                4: { name: "Canon 4", color: "#f39c12" }   // Jaune/orange
            };
            
            // Ajouter le texte de l'arme
            ctx.fillStyle = weaponInfo[currentWeapon].color;
            ctx.font = '12px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(weaponInfo[currentWeapon].name, centerX, centerY + 25);
        }
        
        // Dessiner le cercle d'aide et la ligne de direction
        function drawAim() {
            // Effacer le canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Dessiner le cercle d'aide
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            ctx.strokeStyle = '#3a70d1';
            ctx.lineWidth = 1;
            ctx.stroke();
            
            // Dessiner la ligne de direction
            const radians = currentAngle * Math.PI / 180;
            const endX = centerX + radius * Math.cos(radians);
            const endY = centerY + radius * Math.sin(radians);
            
            // Couleur basée sur l'arme sélectionnée
            const weaponColors = {
                1: '#2ecc71', // Vert
                2: '#e74c3c', // Rouge
                3: '#3498db', // Bleu
                4: '#f39c12'  // Jaune/orange
            };
            
            const lineColor = isFiring ? 
                weaponColors[currentWeapon] : 
                '#7a7a7a';
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(endX, endY);
            ctx.strokeStyle = lineColor;
            ctx.lineWidth = 3;
            ctx.stroke();
            
            // Dessiner le point au bout de la ligne
            ctx.beginPath();
            ctx.arc(endX, endY, 5, 0, 2 * Math.PI);
            ctx.fillStyle = lineColor;
            ctx.fill();
            
            // Dessiner l'angle en texte
            ctx.fillStyle = '#7ab5ff';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(`${Math.round(currentAngle)}°`, centerX, centerY + 5);
            
            // Ajouter les infos sur l'arme
            updateWeaponInfo();
        }
        
        // Calculer l'angle en fonction de la position du clic
        function calculateAngle(x, y) {
            const dx = x - centerX;
            const dy = y - centerY;
            let angle = Math.atan2(dy, dx) * 180 / Math.PI;
            if (angle < 0) angle += 360;
            return angle;
        }
        
        // Démarrer le tir
        function startFiring() {
            if (isFiring) return;
            
            isFiring = true;
            drawAim(); // Redessiner avec la couleur de tir
            
            firingInterval = setInterval(() => {
                if (socket && isConnected) {
                    // Plus simple: envoyer l'angle et l'état du tir
                    socket.emit('rotate_shoot', { 
                        angle: currentAngle,
                        firing: true
                    });
                }
            }, 200);
        }
        
        // Arrêter le tir
        function stopFiring() {
            if (!isFiring) return;
            
            isFiring = false;
            clearInterval(firingInterval);
            firingInterval = null;
            
            // Informer le serveur que le tir est arrêté
            if (socket && isConnected) {
                socket.emit('rotate_shoot', { firing: false });
            }
            
            drawAim(); // Redessiner avec la couleur normale
        }
        
        // Gestionnaire d'événements pour le clic sur le canvas
        canvas.addEventListener('mousedown', function(e) {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            currentAngle = calculateAngle(x, y);
            drawAim();
            startFiring();
        });
        
        canvas.addEventListener('mousemove', function(e) {
            if (!isFiring) return;
            
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            currentAngle = calculateAngle(x, y);
            drawAim();
        });
        
        document.addEventListener('mouseup', function() {
            stopFiring();
        });
        
        // Support tactile
        canvas.addEventListener('touchstart', function(e) {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            const x = touch.clientX - rect.left;
            const y = touch.clientY - rect.top;
            
            currentAngle = calculateAngle(x, y);
            drawAim();
            startFiring();
        });
        
        canvas.addEventListener('touchmove', function(e) {
            if (!isFiring) return;
            e.preventDefault();
            
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            const x = touch.clientX - rect.left;
            const y = touch.clientY - rect.top;
            
            currentAngle = calculateAngle(x, y);
            drawAim();
        });
        
        document.addEventListener('touchend', function() {
            stopFiring();
        });
        
        // Initialiser le dessin
        drawAim();
    }

    setupAimCanvas();
});
