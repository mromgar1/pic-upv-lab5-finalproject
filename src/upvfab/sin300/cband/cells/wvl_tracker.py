from functools import partial

import gdsfactory as gf
from gdsfactory.typings import (
    CrossSectionSpec,
)

from gdsfactory.component import Component
from gdsfactory.typings import CrossSectionSpec, ComponentSpec
from gdsfactory.typings import LayerSpec, Size

from upvfab.sin300.cband.tech import LAYER, TECH


@gf.cell
def mmi2x2(
    width: float | None = None,
    width_taper: float = 1.5,
    length_taper: float = 20.0,
    length_mmi: float = 42.5,
    width_mmi: float = 6.0,
    gap_mmi: float = 0.5,
    cross_section: CrossSectionSpec = "strip",
) -> gf.Component:
    """An mmi2x2.

    An mmi2x2 is a 2x2 splitter

    Args:
        width: the width of the waveguides connecting at the mmi ports
        width_taper: the width at the base of the mmi body
        length_taper: the length of the tapers going towards the mmi body
        length_mmi: the length of the mmi body
        width_mmi: the width of the mmi body
        gap_mmi: the gap between the tapers at the mmi body
        cross_section: a cross section or its name or a function generating a cross section.
    """
    return gf.c.mmi2x2(
        width=width,
        width_taper=width_taper,
        length_taper=length_taper,
        length_mmi=length_mmi,
        width_mmi=width_mmi,
        gap_mmi=gap_mmi,
        cross_section=cross_section,
    )


mmi2x2_rib = partial(mmi2x2, length_mmi=44.8, gap_mmi=0.53, cross_section="rib")

@gf.cell
def mmi3x3(
    width: float | None = None,
    width_taper: float = 1.0,
    length_taper: float = 10.0,
    length_mmi: float = 20.0,
    width_mmi: float = 6.0,
    gap_mmi: float = 0.25,
    taper: ComponentSpec = gf.components.taper,
    straight: ComponentSpec = gf.components.straight,
    cross_section: CrossSectionSpec = "strip",
) -> Component:
    c = gf.Component()

    gap_mmi = gf.snap.snap_to_grid(gap_mmi, grid_factor=2) #ajusta el gap a la rejilla para evitar decimales raros que queden fuera del grid

    x = gf.get_cross_section(cross_section)
    width = width or x.width
    w_taper = width_taper

    _taper = gf.get_component(
        taper,
        length=length_taper,
        width1=width,
        width2=w_taper,
        cross_section=cross_section,
    )

    pitch = w_taper + gap_mmi

    y_bot = -pitch
    y_mid = 0
    y_top = +pitch

    _ = c << gf.get_component(
        straight,
        length=length_mmi,
        width=width_mmi,
        cross_section=cross_section,
    )

    temp_component = Component() #para definir los puertos ideales (temporales)

    ports = [
        temp_component.add_port(
            name="o1",
            orientation=180,
            center=(0, y_bot),
            width=w_taper,
            cross_section=x,
        ),
        temp_component.add_port(
            name="o2",
            orientation=180,
            center=(0, y_mid),
            width=w_taper,
            cross_section=x,
        ),
        temp_component.add_port(
            name="o3",
            orientation=180,
            center=(0, y_top),
            width=w_taper,
            cross_section=x,
        ),
        temp_component.add_port(
            name="o4",
            orientation=0,
            center=(length_mmi, y_top),
            width=w_taper,
            cross_section=x,
        ),
        temp_component.add_port(
            name="o5",
            orientation=0,
            center=(length_mmi, y_mid),
            width=w_taper,
            cross_section=x,
        ),
        temp_component.add_port(
            name="o6",
            orientation=0,
            center=(length_mmi, y_bot),
            width=w_taper,
            cross_section=x,
        ),
    ]

    for port in ports:
        taper_ref = c << _taper
        taper_ref.connect(
            port="o2",
            other=port,
            allow_width_mismatch=True,
        )
        c.add_port(name=port.name, port=taper_ref.ports["o1"])

    c.flatten()
    return c

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
    PDK = gf.get_active_pdk()
    PDK.activate()
    c = gf.path.extrude(P, cross_section=layer)
 
    spr_length = P.length()
    c.info["length"] = float(gf.snap.snap_to_grid(spr_length))
    c.info["lx_final"] = float(lx.length())
 
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

@gf.cell
def bend_euler(
    radius: float = TECH.radius_strip,
    angle: float = 90,
    p: float = 0.5,
    width: float | None = None,
    cross_section: CrossSectionSpec = "strip",
    allow_min_radius_violation: bool = False,
) -> gf.Component:
    """Regular degree euler bend.

    Args:
        radius: in um. Defaults to cross_section_radius.
        angle: total angle of the curve.
        p: Proportion of the curve that is an Euler curve.
        width: width to use. Defaults to cross_section.width.
        cross_section: specification (CrossSection, string, CrossSectionFactory dict).
        allow_min_radius_violation: if True allows radius to be smaller than cross_section radius.
    """
    return gf.c.bend_euler(
        radius=radius,
        angle=angle,
        p=p,
        width=width,
        cross_section=cross_section,
        allow_min_radius_violation=allow_min_radius_violation,
        with_arc_floorplan=True,
        npoints=None,
        layer=None,
    )


@gf.cell
def bend_s(
    size: Size = (50, 10),
    cross_section: CrossSectionSpec = "strip",
    width: float | None = None,
    allow_min_radius_violation: bool = False,
) -> gf.Component:
    """Return S bend with bezier curve.

    stores min_bend_radius property in self.info['min_bend_radius']
    min_bend_radius depends on height and length

    Args:
        size: in x and y direction.
        cross_section: spec.
        width: width of the waveguide. If None, it will use the width of the cross_section.
        allow_min_radius_violation: allows min radius violations.
    """
    return gf.c.bend_s(
        size=size,
        cross_section=cross_section,
        npoints=99,
        allow_min_radius_violation=allow_min_radius_violation,
        width=width,
    )

#########################################################################################
#CIRCUITO PRINCIPAL
#########################################################################################


# N espiral TIENE QUE SER PAR
def wvl_tracker(length_spiral: float = 2152.431640625, length_mmi_2x2: float = 262.9723, taper_width_mmi_2x2: float = 2.8, gap_mmi_2x2: float = 0.5,  taper_length = 10,   length_mmi_3x3: float =  242.4723, taper_width_mmi_3x3: float = 2.8, gap_mmi_3x3: float = 0.2,  AL: float = 56000): #mejorarlo poniendo las funciones de espiral dentro
    c = gf.Component()
   
    mmi_95 = c << mmi2x2(0.45, taper_width_mmi_2x2, taper_length, length_mmi_2x2, 10, gap_mmi_2x2)
    mmi_33 = c << mmi3x3(width= 0.45, width_taper=taper_width_mmi_3x3, length_taper= taper_length, length_mmi = length_mmi_3x3, width_mmi= 10, gap_mmi = gap_mmi_3x3)
    spiral = c << spiral_upv(radius = 10, N_spr = 10 , d_SPR =10 , dx_SPR= length_spiral, dy_SPR = 10, layer = "strip") # N must BE EVEN 
    b1 = c << bend_s(size = [10, 15], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b2 = c << bend_s(size = [10, 15], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    
    
    h = spiral.ports["o2"].dx - spiral.ports["o1"].dx
    wvg_up = c << gf.components.straight(length = h, cross_section= "strip", width = 0.45)
    f_bend_euler180 = partial(bend_euler,angle=180)
    delay_1 = c << gf.components.delay_snake(length=h/2, length0=0, length2=0, n=2, bend180=f_bend_euler180(), cross_section='strip', width = 0.45)
    delay_2 = c << gf.components.delay_snake(length=h/2, length0=0, length2=0, n=2, bend180=f_bend_euler180(), cross_section='strip', width = 0.45)

    dy_mmi95 = mmi_95.ports["o3"].dy - mmi_95.ports["o4"].dy #para conectar los s_bend de forma que las entradas a los mmi queden a la misma altura
    dy_mmi33 = mmi_33.ports["o3"].dy - mmi_33.ports["o1"].dy
    h_bends_33 = (2*15 + dy_mmi95 - dy_mmi33)/2
    b3 = c << bend_s(size = [10, h_bends_33], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b4 = c << bend_s(size = [10, h_bends_33], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    

    delay_1.mirror_x().mirror_y()
    delay_1.dmovex(spiral.ports["o1"].dx ).dmovey(spiral.ports["o1"].dy) 
    delay_2.mirror_y()
    delay_2.dmovex(spiral.ports["o2"].dx ).dmovey(spiral.ports["o2"].dy )
    
    b1.mirror_x()
    b1.dmovex(delay_1.ports["o2"].dx).dmovey(delay_1.ports["o2"].dy)
    mmi_95.dmovex(b1.ports["o2"].dx - length_mmi_2x2 - taper_length).dmovey(b1.ports["o2"].dy + taper_width_mmi_2x2/2  + gap_mmi_2x2/2) 
    b2.dmovex(mmi_95.ports["o3"].dx).dmovey(mmi_95.ports["o3"].dy)
    b3.dmovex(delay_2.ports["o2"].dx).dmovey(delay_2.ports["o2"].dy)
    mmi_33.dmovex(b3.ports["o2"].dx + taper_length).dmovey(b3.ports["o2"].dy + taper_width_mmi_3x3 + gap_mmi_3x3 )  
    b4.mirror_x()
    b4.dmovex(mmi_33.ports["o3"].dx).dmovey(mmi_33.ports["o3"].dy)

    wvg_up.dmovex(b2.ports["o2"].dx).dmovey(b2.ports["o2"].dy)

    #bends entrada y salida cto
    b5 = c <<bend_s(size = [10, 15], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b6 = c << bend_s(size = [10, 15], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b5.mirror_x()
    b5.mirror_y()
    b5.dmovex(mmi_95.ports["o1"].dx).dmovey(mmi_95.ports["o1"].dy)
    b6.mirror_x()
    b6.dmovex(mmi_95.ports["o2"].dx).dmovey(mmi_95.ports["o2"].dy)
    b7 = c << bend_s(size = [10, h_bends_33], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b8 = c << bend_s(size = [10, h_bends_33], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    wvg = c << gf.components.straight(10, cross_section = "strip")
    b7.mirror_y()
    b8.dmovex(mmi_33.ports["o4"].dx).dmovey(mmi_33.ports["o4"].dy)
    b7.dmovex(mmi_33.ports["o6"].dx).dmovey(mmi_33.ports["o6"].dy)
    wvg.dmovex(mmi_33.ports["o5"].dx).dmovey(mmi_33.ports["o5"].dy)



    c.add_port(name = "o1", port = b6.ports["o2"], port_type= "optical")
    c.add_port(name = "o2", port = b5.ports["o2"], port_type= "optical")
    c.add_port(name = "o3", port = b8.ports["o2"], port_type= "optical")
    c.add_port(name = "o4", port = wvg.ports["o2"], port_type= "optical")
    c.add_port(name = "o5", port = b7.ports["o2"], port_type= "optical")


    c.info["total_length_device"] = 2*taper_length + length_mmi_2x2 + 2*10 + h  + 2*taper_length + length_mmi_3x3 #2*10 es de los sbends
    c.info["length_short_arm"] = h + 2*10
    c.info["h_bends_33"] = h_bends_33


    return c 

#########################################################################################
#ESTRUCTURAS TEST
#########################################################################################

@gf.cell
def mmi_2x2_test(length_mmi_2x2: float = 262.9723, taper_width_mmi_2x2: float = 2.8, gap_mmi_2x2: float = 0.5,  taper_length = 10):
    c = gf.Component()

    mmi_95 = c << mmi2x2(0.45, taper_width_mmi_2x2, taper_length, length_mmi_2x2, 10, gap_mmi_2x2)
    b1 = c << bend_s(size = [10, 15], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b2 = c << bend_s(size = [10, 15], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b1.mirror_x()
    mmi_95.dmovex(b1.ports["o2"].dx - length_mmi_2x2 - taper_length).dmovey(b1.ports["o2"].dy + taper_width_mmi_2x2/2  + gap_mmi_2x2/2) 
    b2.dmovex(mmi_95.ports["o3"].dx).dmovey(mmi_95.ports["o3"].dy)

    b3 = c << bend_s(size = [10, 15], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b4 = c << bend_s(size = [10, 15], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b3.mirror_x()
    b3.mirror_y()
    b3.dmovex(mmi_95.ports["o1"].dx).dmovey(mmi_95.ports["o1"].dy)
    b4.mirror_x()
    b4.dmovex(mmi_95.ports["o2"].dx).dmovey(mmi_95.ports["o2"].dy)

    c.add_port(name = "o1", port = b4.ports["o2"], port_type = "optical")
    c.add_port(name = "o2", port = b3.ports["o2"], port_type = "optical")
    c.add_port(name = "o3", port = b2.ports["o2"], port_type = "optical")
    c.add_port(name = "o4", port = b1.ports["o1"], port_type = "optical")

    return c

@gf.cell
def mmi_3x3_test(length_mmi_3x3: float =  242.4723, taper_width_mmi_3x3: float = 2.8, gap_mmi_3x3: float = 0.2, taper_length: float = 10, altura_bends: float = 13.649999999999999 ): #altura bends heredado de cto: h_bends_33

    c = gf.Component()

    mmi_33 = c << mmi3x3(width= 0.45, width_taper=taper_width_mmi_3x3, length_taper= taper_length, length_mmi = length_mmi_3x3, width_mmi= 10, gap_mmi = gap_mmi_3x3)
    b1 = c << bend_s(size = [10, altura_bends], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b2 = c << bend_s(size = [10, altura_bends], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b3 = c << bend_s(size = [10, altura_bends], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    b4 = c << bend_s(size = [10, altura_bends], cross_section = "strip", width = 0.45, allow_min_radius_violation = True)
    wvg = c << gf.components.straight(10, cross_section = "strip")
    
    b1.mirror_x()
    b1.mirror_y()
    b1.dmovex(mmi_33.ports["o1"].dx).dmovey(mmi_33.ports["o1"].dy)
    b2.mirror_x()
    b2.dmovex(mmi_33.ports["o3"].dx).dmovey(mmi_33.ports["o3"].dy)
    b3.mirror_y()
    b4.dmovex(mmi_33.ports["o4"].dx).dmovey(mmi_33.ports["o4"].dy)
    b3.dmovex(mmi_33.ports["o6"].dx).dmovey(mmi_33.ports["o6"].dy)
    wvg.dmovex(mmi_33.ports["o5"].dx).dmovey(mmi_33.ports["o5"].dy)

    c.add_port(name = "o1", port = b2.ports["o2"], port_type = "optical")
    c.add_port(name = "o2", port = b1.ports["o2"], port_type = "optical")
    c.add_port(name = "o3", port = b4.ports["o2"], port_type = "optical")
    c.add_port(name = "o4", port = wvg.ports["o2"], port_type = "optical")
    c.add_port(name = "o5", port = b3.ports["o2"], port_type = "optical")

    return c

@gf.cell
def spiral_delays_test(length_spiral: float = 2152.431640625 ):
    c = gf.Component()
    spiral = c << spiral_upv(radius = 10, N_spr = 10 , d_SPR =10 , dx_SPR= length_spiral, dy_SPR = 10, layer = "strip") # N must BE EVEN 
    h = spiral.ports["o2"].dx - spiral.ports["o1"].dx
    f_bend_euler180 = partial(bend_euler,angle=180)
    delay_1 = c << gf.components.delay_snake(length=h/2, length0=0, length2=0, n=2, bend180=f_bend_euler180(), cross_section='strip', width = 0.45)
    delay_2 = c << gf.components.delay_snake(length=h/2, length0=0, length2=0, n=2, bend180=f_bend_euler180(), cross_section='strip', width = 0.45)
    delay_1.mirror_x().mirror_y()
    delay_1.dmovex(spiral.ports["o1"].dx ).dmovey(spiral.ports["o1"].dy) 
    delay_2.mirror_y()
    delay_2.dmovex(spiral.ports["o2"].dx ).dmovey(spiral.ports["o2"].dy )

    c.add_port(name = "o1", port = delay_1.ports["o2"], port_type = "optical")
    c.add_port(name = "o2", port = delay_2.ports["o2"], port_type = "optical")

    return c



