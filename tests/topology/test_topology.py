import os

from tyssue.generation import three_faces_sheet
from tyssue.core.sheet import Sheet

from tyssue.geometry.sheet_geometry import SheetGeometry as geom
from tyssue.topology.base_topology import (
    close_face,
    add_vert,
    condition_4i,
    condition_4ii,
)

from tyssue.stores import stores_dir
from tyssue.io.hdf5 import load_datasets
from tyssue.topology.sheet_topology import cell_division, type1_transition, split_vert
from tyssue.config.geometry import cylindrical_sheet
from tyssue.draw import sheet_view


def test_condition4i():
    sheet = Sheet("test", *three_faces_sheet())
    assert len(condition_4i(sheet)) == 0

    sheet.edge_df = sheet.edge_df.append(sheet.edge_df.iloc[-1], ignore_index=True)
    sheet.edge_df.index.name = "edge"
    sheet.reset_index()
    sheet.reset_topo()
    assert len(condition_4i(sheet)) == 1


def test_condition4ii():
    sheet = Sheet("test", *three_faces_sheet())
    assert len(condition_4ii(sheet)) == 0
    add_vert(sheet, 0)
    sheet.reset_index()
    sheet.reset_topo()
    assert len(condition_4ii(sheet)) == 2


def test_division():

    h5store = os.path.join(stores_dir, "small_hexagonal.hf5")

    datasets = load_datasets(h5store, data_names=["face", "vert", "edge"])
    specs = cylindrical_sheet()
    sheet = Sheet("emin", datasets, specs)
    geom.update_all(sheet)

    Nf, Ne, Nv = sheet.Nf, sheet.Ne, sheet.Nv

    cell_division(sheet, 17, geom)

    assert sheet.Nf - Nf == 1
    assert sheet.Nv - Nv == 2
    assert sheet.Ne - Ne == 6


def test_t1_transition():

    h5store = os.path.join(stores_dir, "small_hexagonal.hf5")
    datasets = load_datasets(h5store, data_names=["face", "vert", "edge"])
    specs = cylindrical_sheet()
    sheet = Sheet("emin", datasets, specs)
    geom.update_all(sheet)
    face = sheet.edge_df.loc[84, "face"]
    type1_transition(sheet, 84)
    assert sheet.face_df.loc[face, "num_sides"] == 5


def test_t1_at_border():
    datasets, specs = three_faces_sheet()
    sheet = Sheet("3cells_2D", datasets, specs)
    geom.update_all(sheet)
    # double half edge with no right cell (aka cell c)
    type1_transition(sheet, 0, multiplier=4.0)
    sheet.reset_index()
    assert sheet.validate()
    geom.update_all(sheet)
    # single half edge with no bottom cell (aka cell d)
    type1_transition(sheet, 16, multiplier=5.0)
    geom.update_all(sheet)
    assert sheet.validate()
    # single half edge with no left cell (aka cell a)
    type1_transition(sheet, 17, multiplier=5.0)
    geom.update_all(sheet)
    assert sheet.validate()


def test_split_vert():

    datasets, specs = three_faces_sheet()
    sheet = Sheet("3cells_2D", datasets, specs)
    geom.update_all(sheet)

    split_vert(sheet, 0, multiplier=10)
    geom.update_all(sheet)
    assert sheet.Nv == 14
    assert sheet.Ne == 20


def test_close_face():
    sheet = Sheet("test", *three_faces_sheet())
    e0 = sheet.edge_df.index[0]
    face = sheet.edge_df.loc[e0, "face"]
    Ne = sheet.Ne
    sheet.edge_df = sheet.edge_df.loc[sheet.edge_df.index[1:]].copy()
    close_face(sheet, face)
    assert sheet.Ne == Ne

    close_face(sheet, face)
    assert sheet.Ne == Ne


def test_merge_border_edges():
    sheet = Sheet.planar_sheet_3d("sheet", 5, 6, 1, 1)
    sheet.get_opposite()
    sheet.sanitize(trim_borders=True)
    assert (
        sheet.edge_df[sheet.edge_df["opposite"] < 0]
        .groupby("face")["opposite"]
        .sum()
        .min()
        == -1
    )
    assert not set(sheet.vert_df.index).difference(sheet.edge_df.srce)
