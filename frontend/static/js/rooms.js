document.addEventListener('DOMContentLoaded', () => {
    document.getElementById("logout-btn").addEventListener("click", logout);
    document.getElementById("create-room-btn").addEventListener("click", showPopup);
    document.getElementById("cancel-btn").addEventListener("click", closePopup);
    document.getElementById("create-btn").addEventListener("click", createRoom);
    fetchUserRooms()
})

document.addEventListener('keydown', e => {
    if (e.key === 'Enter' && document.getElementById('create-room-popup').style.display === 'flex') {
        createRoom()
    }
})

function showPopup() {
    document.getElementById("create-room-popup").style.display = "flex"
}

function closePopup() {
    const popup = document.getElementById("create-room-popup")
    popup.style.display = "none"
    popup.querySelectorAll('input').forEach(input => input.value = "")
    document.getElementById("room-type").value = "public"
    document.getElementById("password-field").classList.add("hidden")
    document.getElementById("password").disabled = true
}

function createRoom() {
    const nameField = document.querySelector('#name-field')
    const passwordField = document.querySelector('#password-field')

    const name = nameField.querySelector('input').value
    const type = document.getElementById("room-type").value
    const password = passwordField.querySelector('input').value
    nameField.classList.toggle('error', !name)
    passwordField.classList.toggle('error', type === "private" && !password)

    if (name && (password || type === "public")) {
        const payload = {name, type}
        payload.password = (type === 'private') ? password : null;

        fetch('/api/rooms/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload),
            credentials: 'include'
        })
            .then(r => r.ok ? r.json() : Promise.reject())
            .then(data => {
                addRoomToList(data)
                closePopup()
                location.href = `/rooms/${data.id}`
            })
            .catch(() => {
                document.querySelector('#create-room-popup .global-error').textContent = 'Failed to create room'
            })
    }
}

window.onclick = function (event) {
    const modal = document.getElementById("create-room-popup")
    if (event.target === modal) closePopup()
}

function roomTypeChanged(element) {
    const isPrivate = element.value === "private"
    const passwordField = document.getElementById("password-field")
    const passwordInput = document.getElementById("password")
    passwordField.classList.toggle('hidden', !isPrivate)
    passwordInput.disabled = !isPrivate
    if (!isPrivate) passwordInput.value = "";
}

function addRoomToList(room) {
    const roomsGrid = document.querySelector('.rooms-grid')
    const roomCard = document.createElement('div')
    roomCard.className = 'room-card'

    const roomName = document.createElement('h4')
    roomName.textContent = room.name
    roomCard.appendChild(roomName)

    const joinButton = document.createElement('button')
    joinButton.className = 'join-btn'
    joinButton.textContent = 'Join'
    joinButton.onclick = () => location.href = `/rooms/${room.id}`
    roomCard.appendChild(joinButton)

    const deleteButton = document.createElement('button')
    deleteButton.className = 'delete-btn'
    deleteButton.textContent = 'Delete'

    deleteButton.onclick = async () => {
        try {
            const deleteResponse = await fetch(`/api/rooms/${room.id}`, {
                method: 'DELETE',
                credentials: 'include'
            })
            if (deleteResponse.ok) {
                roomCard.remove()
            } else {
                console.error('Failed to delete room')
            }
        } catch {
            console.error('Failed to delete room')
        }
    }
    roomCard.appendChild(deleteButton)
    roomsGrid.appendChild(roomCard)
}

async function fetchUserRooms() {
    try {
        const response = await fetch('/api/rooms/', {
            method: 'GET',
            credentials: 'include'
        })

        if (response.ok) {
            const roomsData = await response.json()
            const roomsGrid = document.querySelector('.rooms-grid')

            roomsGrid.innerHTML = ''

            roomsData.forEach(room => addRoomToList(room))
        }
    } catch {
        console.error('Failed to load rooms')
    }
}

async function logout() {
    const response = await fetch('/api/users/logout', {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
        }
    });
    if (response.ok) {
        window.location.href = '/';
    } else {
        console.error('Logout failed', response.status);
    }
}
