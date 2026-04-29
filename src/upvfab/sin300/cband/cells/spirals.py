"""Rings."""

import gdsfactory as gf
from gdsfactory.typings import (
    ComponentSpec,
    CrossSectionSpec,
    Floats,
)


@gf.cell
def spiral(
    length: float = 100,
    cross_section: CrossSectionSpec = "strip",
    spacing: float = 3,
    n_loops: int = 6,
) -> gf.Component:
    """Returns a spiral double (spiral in, and then out).

    Args:
        length: length of the spiral straight section.
        cross_section: cross_section component.
        spacing: spacing between the spiral loops.
        n_loops: number of loops.
    """
    return gf.c.spiral(
        length=length,
        cross_section=cross_section,
        spacing=spacing,
        n_loops=n_loops,
        bend="bend_euler",
        straight="straight",
    )


# @gf.cell
# def spiral_racetrack(
#     min_radius: float | None = None,
#     straight_length: float = 200.0,
#     spacings: Floats = (10, 10, 15, 15, 10, 10),
#     straight: ComponentSpec = "straight",
#     bend: ComponentSpec = "bend_euler",
#     bend_s: ComponentSpec = "bend_s",
#     cross_section: CrossSectionSpec = "strip",
#     cross_section_s: CrossSectionSpec | None = None,
#     extra_90_deg_bend: bool = False,
#     allow_min_radius_violation: bool = False,
# ) -> gf.Component:
#     """Returns Racetrack-Spiral.

#     Args:
#         min_radius: smallest radius in um.
#         straight_length: length of the straight segments in um.
#         spacings: space between the center of neighboring waveguides in um.
#         straight: factory to generate the straight segments.
#         bend: factory to generate the bend segments.
#         bend_s: factory to generate the s-bend segments.
#         cross_section: cross-section of the waveguides.
#         cross_section_s: cross-section of the s bend waveguide (optional).
#         extra_90_deg_bend: if True, we add an additional straight + 90 degree bent at the output, so the output port is looking down.
#         allow_min_radius_violation: if True, will allow the s-bend to have a smaller radius than the minimum radius.
#     """
#     return gf.c.spiral_racetrack(
#         min_radius=min_radius,
#         straight_length=straight_length,
#         spacings=spacings,
#         straight=straight,
#         bend=bend,
#         bend_s=bend_s,
#         cross_section=cross_section,
#         cross_section_s=cross_section_s,
#         extra_90_deg_bend=extra_90_deg_bend,
#         allow_min_radius_violation=allow_min_radius_violation,
#     )


# @gf.cell
# def spiral_racetrack_fixed_length(
#     min_radius: float | None = None,
#     in_out_port_spacing: float = 500,
#     n_straight_sections: float = 10,
#     length: float = 7000.0,
#     min_spacing: float = 5.0,
#     straight: ComponentSpec = "straight",
#     bend: ComponentSpec = "bend_euler",
#     bend_s: ComponentSpec = "bend_s",
#     cross_section: CrossSectionSpec = "strip",
#     cross_section_s: CrossSectionSpec | None = None,
# ) -> gf.Component:
#     """Returns Racetrack-Spiral.

#     Args:
#         min_radius: smallest radius in um.
#         straight_length: length of the straight segments in um.
#         spacings: space between the center of neighboring waveguides in um.
#         straight: factory to generate the straight segments.
#         bend: factory to generate the bend segments.
#         bend_s: factory to generate the s-bend segments.
#         cross_section: cross-section of the waveguides.
#         cross_section_s: cross-section of the s bend waveguide (optional).
#         extra_90_deg_bend: if True, we add an additional straight + 90 degree bent at the output, so the output port is looking down.
#         allow_min_radius_violation: if True, will allow the s-bend to have a smaller radius than the minimum radius.
#     """
#     return gf.c.spiral_racetrack_fixed_length(
#         min_radius=min_radius,
#         in_out_port_spacing=in_out_port_spacing,
#         length=length,
#         min_spacing=min_spacing,
#         straight=straight,
#         bend=bend,
#         bend_s=bend_s,
#         cross_section=cross_section,
#         cross_section_s=cross_section_s,
#     )


@gf.cell
def spiral_racetrack_heater(
    spacing: float = 10,
    num: int = 5,
    straight_length: float = 200,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """Returns spiral racetrack with a heater above.

    based on https://doi.org/10.1364/OL.400230 .

    Args:
        spacing: center to center spacing between the waveguides.
        num: number of spiral loops.
        straight_length: length of the straight segments.
        cross_section: cross_section.
    """
    return gf.c.spiral_racetrack_heater_metal(
        straight_length=straight_length,
        min_radius=None,
        spacing=spacing,
        num=num,
        straight="straight",
        bend="bend_euler",
        bend_s=gf.get_cell("bend_s"),
        waveguide_cross_section=cross_section,
        via_stack="via_stack_heater_mtop",
    )
from functools import partial

@gf.cell
def spiral_upv(
    radius: float = 100.0,
    N_spr: int = 5,
    d_SPR: float = 7.0,
    dx_SPR: float = 10.0,
    dy_SPR: float = 10.0,
    layer: CrossSectionSpec = "strip",
    ) -> gf.Component:
   
    """Returns a spiral.
 
    Pending: add ports, check whether it works as other (native) spirals
    Use partial with this?
 
    Args:
        radius: spiral radius.
        N_spr: order-number of loops (0,1,...)
        d_SPR: waveguide separation
        dx_SPR: spiral straight extent in x
        dy_SPR: spiral straight extent in y
        layer: extruding in a specified layer (or cross section)
    """
 
    # Path definitions
    P = gf.Path()
    P1 = gf.Path()
    P2 = gf.Path()
 
    # Involed lengths
    lx0 = gf.path.straight(dx_SPR + d_SPR + 2*radius)
    ldy = gf.path.straight(dy_SPR)
    ld = gf.path.straight(d_SPR)
    ly0 = ldy+ld
 
    # 90 degree curves
    parcL = gf.path.arc(radius=radius, angle=90)
    parcR = gf.path.arc(radius=radius, angle=-90)
 
    # Zero-th order
    P01 = ld+ld + ly0 + parcL + lx0 + parcL + ly0 + parcL + gf.path.straight(dx_SPR/2)
    P02 = gf.path.straight(dx_SPR/2) + parcR + ly0
    P0 =  P01 + parcL + ldy + parcR + P02
 
    P = P0
    lx = lx0
    ly = ly0 + ld + ld
 
    # Generating loops
    for i in range(1,N_spr+1):
   
        if i == N_spr:
            if i % 2 == 1:
             P1 = parcR + (lx) + parcR + (ly) + parcR + (lx+ld+ld) + parcR + (ly+ld)
             P = P + P1
            else:
             P1 = (ly+ld) + parcL + (lx+ld+ld) + parcL + (ly) + parcL + (lx) + parcL
             P = P1 + P
        else:  
            if i % 2 == 1:
             P1 = parcR + (lx) + parcR + (ly) + parcR + (lx+ld+ld) + parcR + (ly+ld+ld)
             P = P + P1
            else:
             P1 = (ly+ld+ld) + parcL + (lx+ld+ld) + parcL + (ly) + parcL + (lx) + parcL
             P = P1 + P
       
        lx = lx + ld + ld
        ly = ly + ld + ld
 
   
    # End feet
    if N_spr % 2 == 1: P =  (lx + parcL) + P + parcL
    else: P =  parcR + P + (parcR + lx)
 
    # f = P.plot()
 
    # if N_spr % 2 == 0:
        # P = P.rotate(90)
        # P = P.()
        # P = P.(
        # p1=(0, 1), p2=(0, 0))
 
    # Extrude
    c = gf.path.extrude(P, cross_section=layer)
 
    spr_length = P.length()
    c.info["length"] = float(gf.snap.snap_to_grid(spr_length))
 
    return c

from scipy.optimize import minimize
import numpy as np
 
def define_spiral_length(delay_length=10000,
                         N_spr=7,
                         radius=100,
                         d_SPR=10,
                         dy_SPR=20,
                         ):
    """Defines the spiral straight length based on the desired delay_length"""
    print("Defining spiral length for delay:", delay_length)
    def f(x):
        spiral_to_test = partial(spiral_upv, N_spr=N_spr ,dx_SPR=x[0], radius=radius, d_SPR=d_SPR, dy_SPR=dy_SPR)
        device = spiral_to_test()
        current_delay_length = device.info["length"]
        #print("Current spiral length:", current_delay_length, "for dx_SPR:", x[0])
        cost = current_delay_length - delay_length
        return np.abs(cost)
    length_spiral = minimize(f, x0=np.array(200.0), method='Nelder-Mead',tol=1e-2, bounds=((10, 5000.0),)).x[0]
    print("Spiral length set to:", length_spiral)
    return length_spiral






if __name__ == "__main__":
    from upvfab.sin300.cband import PDK

    PDK.activate()
    c = spiral()
    c.show()
