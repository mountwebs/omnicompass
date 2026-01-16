# Omni-Compass Architecture Plan
## 1. Backend (Python + Skyfield)

Core Functionality:
The backend will be a Python application using the Skyfield library. Skyfield will handle astronomical computations, like calculating the position of the Sun (or other celestial bodies later on). Essentially, the backend will:

Receive a request for a particular celestial object (initially the Sun).

Compute its current position in the sky based on the user's location and time.

Serve this data via a WebSocket connection to the frontend.

Switching Between Objects:
Later on, the backend will also handle switching between different celestial objects (like Mars). This can be done by providing an endpoint or a command over the WebSocket that changes the "target" object.

## 2. Frontend (Vite + Three.js)

User Interface:
The frontend will be a web application built with Vite for a modern and fast development environment. It will use Three.js to render a 3D arrow. This arrow will visually point towards the Sun (or whichever object is selected). Use the arrow in assets/arrow.fbx.

User Controls:
Users will be able to input their geographic location and the orientation of their device or screen. The frontend will send this information to the backend and receive real-time updates about the Sun’s position.

## 3. WebSocket Communication

Real-Time Updates:
A WebSocket connection will be established between the frontend and the backend. This allows the backend to push updates to the frontend whenever the Sun’s position changes significantly. This way, the arrow in the Three.js scene will always point correctly.

Switching Targets:
When you want to switch from tracking the Sun to tracking Mars (or any other object), the frontend can send a command to the backend over the WebSocket. The backend will then adjust its calculations and push the new directional data to the frontend.

Summary

In short, you'll have a Python backend using Skyfield to compute celestial positions, a Vite + Three.js frontend to visualize a 3D arrow pointing at the target object, and a WebSocket layer in between for real-time updates and command handling. This should give you a solid foundation to build on!