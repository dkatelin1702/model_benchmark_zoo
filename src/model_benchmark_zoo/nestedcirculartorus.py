
class Nestedcirculartorus:
    def __init__(self, materials, major_radius=10, outer_minor_radius=4, inner_minor_radius=3):
        
        if outer_minor_radius<=inner_minor_radius:
            raise ValueError('outer_minor_radius should be greater than inner_minor_radius')

        self.major_radius = major_radius
        self.outer_minor_radius = outer_minor_radius
        self.inner_minor_radius = inner_minor_radius
        self.materials = materials

    def csg_model(self):
        import openmc
        
        outer_surface = openmc.ZTorus(a=self.major_radius, b=self.outer_minor_radius, c=self.outer_minor_radius, boundary_type="vacuum")
        inner_surface = openmc.ZTorus(a=self.major_radius, b=self.inner_minor_radius, c=self.inner_minor_radius, boundary_type="vacuum")
    
        outer_region = -outer_surface
        inner_region = -inner_surface

        outer_cell = openmc.Cell(region=outer_region & ~ inner_region)
        inner_cell = openmc.Cell(region=inner_region)

        geometry = openmc.Geometry([cell_1, cell_2])
        model = openmc.Model(geometry=geometry)
        return model

    def cadquery_assembly(self):
        import cadquery as cq
        assembly = cq.Assembly(name="nestedcirculartorus")
        innercirculartorus1 = cq.Workplane("XZ", origin=(10, 0, 0)).circle(3).revolve(180, (-10,0,0), (-10,1,0))
        innercirculartorus2 = cq.Workplane("XZ", origin=(-10, 0, 0)).circle(3).revolve(180, (10,0,0), (10,1,0))
        outercirculartorus1 = cq.Workplane("XZ", origin=(10, 0, 0)).circle(4).revolve(180, (-10,0,0), (-10,1,0)).cut(innercirculartorus1)
        outercirculartorus2 = cq.Workplane("XZ", origin=(-10, 0, 0)).circle(4).revolve(180, (10,0,0), (10,1,0)).cut(innercirculartorus2)
        innercirculartorus = innercirculartorus1.union(innercirculartorus2, clean=False)
        outercirculartorus = outercirculartorus1.union(outercirculartorus2, clean=False)
        
        assembly.add(innercirculartorus)
        assembly.add(outercirculartorus)
        return assembly

    def export_stp_file(self, filename="nestedcirculartorus.step"):
        self.cadquery_assembly().save(filename, "STEP")

    def dagmc_model(self, filename="nestedcirculartorus.h5m", min_mesh_size=0.1, max_mesh_size=100.0):
        from cad_to_dagmc import CadToDagmc
        import openmc
        
        assembly = self.cadquery_assembly()
        ctd = CadToDagmc()
        material_tags = [self.materials[0].name, self.materials[1].name]
        ctd.add_cadquery_object(assembly, material_tags=material_tags)
        ctd.export_dagmc_h5m_file(
            filename=filename,
            min_mesh_size=min_mesh_size,
            max_mesh_size=max_mesh_size,
            msh_filename='nestedcirculartorus.msh'  # this arg allows the gmsh file to be written out
        )
        universe = openmc.DAGMCUniverse(filename).bounded_universe()
        geometry = openmc.Geometry(universe)
        model = openmc.Model(geometry=geometry)
        return model
