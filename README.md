# README

Blender add-on for automated generation of Brick sculptures and simulations from mesh objects (Blender version: 2.79)

## Bricker
  * Features:
      * Convert any 3D Mesh into a photo-real 3D brick model
      * Generate animated brick models from keyframed animation, simulations (soft body physics, fluid, cloth, etc), armature, and much more
      * Adjust model settings after it's been created
      * Customize the model after it's been auto-generated using handy tools like split bricks, merge bricks, add adjacent bricks, change brick type, and more!
  * Instructions:
      * Create a new model with the 'New Model' button, and name it whatever you'd like
      * Select a source object with the 'Source Object' eyedropper (defaults to active object when model was created)
      * Click 'Brickify Object'
      * Adjust model settings for your desired result
      * Click 'Update Model' to view setting adjustments
      * Once you're satisfied with the settings, make adjustments to your model in the 'Customize Model' dropdown menu
  * Future improvements:
      * Add mode for selecting verts at locations next to bricks and adding bricks there
      * For animation, if last frame's brickFreqMatrix matches current frame's brickFreqMatrix, save time by just keeping that model around for another frame or duplicating it for the next frame or something
      * New feature: SNOT (studs not on top) functionality
      * Add 'exclusion' functionality so that one model doesn’t create bricks where another model already did
      * Add many more brick types, including inverted slopes
      * Generate model with bricks and slopes to more closely approximate original mesh
      * Transfer matObj functionality to new custom list property
      * Add customization for custom object offset, size, and brick scale (amount of bricksDict locations it takes up), default to scale/offset for 1x1 brick with stud
      * Alternate merge directions per level for greedy merge type
      * Add 'select bricks' button in Brick Models dropdown arrow
  * Known issues:
      * For models with thin outer shells, Bricker may use color of inside face instead of outside face for brick material (see snapchat hotdog file)
      * Applying model rotation when deleting brickified model whose source has rotated parent produces problematic results
      * In 'Realistic Creek 4' file, Bricker doesn't know which images to use, and simply uses the active UV Map instead of intelligently selecting the UV map affecting that face_idx.
