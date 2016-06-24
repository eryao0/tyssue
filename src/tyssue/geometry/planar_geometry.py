import numpy as np

from .base_geometry import BaseGeometry


class PlanarGeometry(BaseGeometry):
    """Geomtetry methods for 2D planar cell arangements
    """
    @classmethod
    def update_all(cls, sheet):
        '''
        Updates the sheet geometry by updating:
        * the edge vector coordinates
        * the edge lengths
        * the face centroids
        * the normals to each edge associated face
        * the face areas
        '''

        cls.update_dcoords(sheet)
        cls.update_length(sheet)
        cls.update_centroid(sheet)
        cls.update_normals(sheet)
        cls.update_areas(sheet)
        cls.update_perimeters(sheet)

    @staticmethod
    def update_perimeters(sheet):
        '''
        Updates the perimeter of each face.
        '''
        sheet.face_df['perimeter'] = sheet.sum_face(sheet.edge_df['length'])

    @staticmethod
    def update_normals(sheet):

        coords = sheet.coords
        face_pos = sheet.upcast_face(sheet.face_df[coords]).values
        srce_pos = sheet.upcast_srce(sheet.vert_df[coords]).values
        trgt_pos = sheet.upcast_trgt(sheet.vert_df[coords]).values

        normals = np.cross(srce_pos - face_pos, trgt_pos - srce_pos)
        sheet.edge_df["nz"] = normals

    @staticmethod
    def update_areas(sheet):
        '''
        Updates the normal coordniate of each (srce, trgt, face) face.
        '''
        sheet.edge_df['sub_area'] = np.abs(sheet.edge_df['nz']) / 2
        sheet.face_df['area'] = sheet.sum_face(sheet.edge_df['sub_area'])
