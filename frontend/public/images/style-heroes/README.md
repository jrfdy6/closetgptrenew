# Style Hero Images

This directory contains the hero images for each style archetype used in the quiz results page.

## Required Images

Based on the reference images provided, you need to add these images:

### 1. The Strategist - Conference Room
- **File**: `strategist-conference-room.jpg`
- **Description**: Diverse group of professionals in a modern office conference room, actively collaborating on a business presentation around a glass table with laptops and documents
- **Reference**: Conference room image with people pointing at charts and taking notes

### 2. The Innovator - Art Gallery  
- **File**: `innovator-art-gallery.jpg`
- **Description**: Creative professionals in a contemporary art gallery, actively collaborating on an art installation with easels, palettes, and painting supplies
- **Reference**: Art gallery image with people painting and photographing

### 3. The Classic - Afternoon Tea
- **File**: `classic-afternoon-tea.jpg`
- **Description**: Elegant professionals in a luxurious hotel lounge, engaged in refined business discussion over afternoon tea with architectural blueprints
- **Reference**: Afternoon tea image with people around marble table with blueprints

### 4. The Wanderer - Bohemian Nature
- **File**: `wanderer-bohemian-nature.jpg`
- **Description**: Free-spirited individuals in a natural outdoor setting, actively creating community art with easels, guitars, and natural materials
- **Reference**: Bohemian nature image with people painting and playing music outdoors

### 5. The Rebel - Graffiti Alley
- **File**: `rebel-graffiti-alley.jpg`
- **Description**: Alternative individuals in an urban street setting, actively creating street art mural with spray cans and ladders
- **Reference**: Graffiti alley image with people spray-painting on brick walls

### 6. The Connoisseur - Wine Tasting
- **File**: `connoisseur-wine-tasting.jpg`
- **Description**: Sophisticated professionals in a luxury wine cellar, actively participating in wine tasting and education with bottles and glasses
- **Reference**: Wine tasting image with people around dark wooden table

### 7. The Modernist - Office Meeting
- **File**: `modernist-office-meeting.jpg`
- **Description**: Contemporary professionals in a minimalist office, actively working on design projects with clean lines and modern furniture
- **Reference**: Modern office meeting image (can use strategist image as base)

### 8. The Architect - Blueprint Meeting
- **File**: `architect-blueprint-meeting.jpg`
- **Description**: Professional architects in a modern office, actively reviewing blueprints and 3D models around a white conference table
- **Reference**: Blueprint meeting image with people examining 3D models

## Image Specifications

- **Dimensions**: 1920x1080px (16:9 aspect ratio)
- **Format**: JPG or PNG
- **Quality**: High-resolution, professional photography
- **Style**: Editorial fashion photography aesthetic
- **Content**: Diverse groups of 4-5 people actively engaged in relevant activities

## Usage

These images are automatically loaded based on the user's style archetype in the quiz results page. The `getHeroImageForPersona()` function maps each persona ID to its corresponding hero image.

## Fallback

If an image is missing, the system will fall back to `default-hero.jpg` (not included - you may want to add a generic professional group image as fallback).
