bl_info = {
    "name": "Cycles Ray Visibility Lister",
    "description": "Manage Cycles ray visibility settings for objects in a scene",
    "author": "Odilkhan Yakubov (odil24)",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "category": "3D View",
}
import bpy

# Custom UIList for object display with icon-based toggles
class OBJECT_UL_RayVisibilityList(bpy.types.UIList):
    bl_idname = "OBJECT_UL_RayVisibilityList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_prop, index):
        obj = item

        # Determine if the object is selected (active) in the 3D view
        is_active = obj == context.view_layer.objects.active

        # Set the row background color if the object is selected (highlighted)
        row = layout.row(align=True)
        
        # Check if the object is active (selected in the 3D view)
        if is_active:
            row.alert = True  # Highlight the row with a different background color
            row.operator("object.select_object_in_list", text=obj.name, icon='CHECKMARK').obj_name = obj.name
            row.scale_x = 2  # Make the label larger for better visibility
        else:
            row.alert = False  # No highlight for non-selected objects
            row.operator("object.select_object_in_list", text=obj.name, icon='CHECKMARK').obj_name = obj.name
            row.scale_x = 2  # Maintain the same scale for non-selected objects

        # Show icon-based visibility toggles for each ray visibility type
        row = layout.row(align=True)

        # Camera visibility toggle
        row.prop(obj, "visible_camera", text="", icon='RESTRICT_RENDER_OFF' if obj.visible_camera else 'RESTRICT_RENDER_ON', emboss=False)
        row.separator()  # Adds a vertical line (separation) between the first and second toggle
        
        # Diffuse visibility toggle
        row.prop(obj, "visible_diffuse", text="",  icon='INDIRECT_ONLY_ON' if obj.visible_diffuse else 'INDIRECT_ONLY_OFF', emboss=False)
        row.separator()  # Vertical line between diffuse and glossy visibility
        
        # Glossy visibility toggle
        row.prop(obj, "visible_glossy", text="",  icon='PROP_ON' if obj.visible_glossy else 'PROP_OFF', emboss=False)
        row.separator()  # Vertical line between glossy and transmission visibility
        
        # Transmission visibility toggle
        row.prop(obj, "visible_transmission", text="",  icon='CLIPUV_DEHLT' if obj.visible_transmission else 'CLIPUV_HLT', emboss=False)
        row.separator()  # Vertical line between transmission and volume scatter visibility
        
        # Volume Scatter visibility toggle
        row.prop(obj, "visible_volume_scatter", text="",  icon='OUTLINER_OB_VOLUME' if obj.visible_volume_scatter else 'VOLUME_DATA', emboss=False)
        row.separator()  # Vertical line between volume scatter and shadow visibility
        
        # Shadow visibility toggle
        row.prop(obj, "visible_shadow", text="",  icon='GHOST_ENABLED' if obj.visible_shadow else 'GHOST_DISABLED', emboss=False)

# Operator to select object when clicked in the list
class OBJECT_OT_SelectObjectInList(bpy.types.Operator):
    bl_idname = "object.select_object_in_list"
    bl_label = "Select Object in List"
    obj_name: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj_name)
        if obj:
            # Deselect all objects and select the clicked object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)

            # Set the active object in the 3D View
            context.view_layer.objects.active = obj

        return {'FINISHED'}

class OBJECT_PT_RayVisibilityPanel(bpy.types.Panel):
    bl_label = "Cycles Ray Visibility Lister"
    bl_idname = "OBJECT_PT_ray_visibility"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Ray Visibility'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # Filter to include only mesh objects (exclude lights, cameras, and empties)
        mesh_objects = [obj for obj in scene.objects if obj.type == 'MESH']
        
        # Display total number of mesh objects in the scene
        layout.label(text=f"Mesh Counts in Scene: {len(mesh_objects)}")

        # Create a scrolling area for all mesh objects using a custom UIList
        box = layout.box()
        box.scale_y = 1.2  # Slightly increase the vertical scale for better spacing
        
        # Use the custom UIList to display mesh objects in a scrollable list
        row = box.row()
        row.template_list("OBJECT_UL_RayVisibilityList", "", scene, "objects", context.scene, "object_index", rows=10)

def init_object_properties(scene, context):
    # This function will initialize the visibility properties for all objects after Blender has fully loaded the scene
    for obj in bpy.data.objects:
        if not hasattr(obj, "visible_camera"):
            obj["visible_camera"] = True
        if not hasattr(obj, "visible_diffuse"):
            obj["visible_diffuse"] = True
        if not hasattr(obj, "visible_glossy"):
            obj["visible_glossy"] = True
        if not hasattr(obj, "visible_transmission"):
            obj["visible_transmission"] = True
        if not hasattr(obj, "visible_volume_scatter"):
            obj["visible_volume_scatter"] = True
        if not hasattr(obj, "visible_shadow"):
            obj["visible_shadow"] = True

def register():
    bpy.types.Scene.object_index = bpy.props.IntProperty(name="Object Index", default=0)
    
    bpy.utils.register_class(OBJECT_UL_RayVisibilityList)
    bpy.utils.register_class(OBJECT_PT_RayVisibilityPanel)
    bpy.utils.register_class(OBJECT_OT_SelectObjectInList)

    # Initialize object properties after the addon is fully registered and the data is available
    bpy.app.handlers.load_post.append(init_object_properties)  # This will ensure that the properties are added after loading

def unregister():
    bpy.app.handlers.load_post.remove(init_object_properties)  # Remove the handler to prevent duplicate calls

    del bpy.types.Scene.object_index
    bpy.utils.unregister_class(OBJECT_UL_RayVisibilityList)
    bpy.utils.unregister_class(OBJECT_PT_RayVisibilityPanel)
    bpy.utils.unregister_class(OBJECT_OT_SelectObjectInList)

if __name__ == "__main__":
    register()
