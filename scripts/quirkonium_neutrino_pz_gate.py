#!/usr/bin/env python3
"""No-detector neutrino-pz ambiguity pilot for squirkonium WZ->e+nu mu+mu-.

Research question: can a *kinematic prescription* preserve the sign of the
model-specific joint W/Z decay-plane cos(Phi) interference?

Generate on-shell 2->4 angular configurations weighted by the analytic
WZ spin density. Orient W randomly relative to the proton beam
(using isotropic polar quadrature), and apply illustrative longitudinal
resonance boosts (NOT a validated rapidity distribution).
Use exact neutrino pT, the true W mass, and solve the two quadratic
neutrino pz solutions. Compare:

* truth neutrino pz: validation closure;
* root with the smaller |pz|: a transparent but not optimized prescription;
* root with m(e+nu+mu+mu-) closest to known M: OPTIMISTIC, uses the known
  signal mass and is not model-independent;
* equal average of the two solutions: sensitivity to ambiguity.

All 4-momenta are exact: no pT resolution, no detector/FSR, no backgrounds,
no fiducial selection, no full quirk production and no event samples.
Generated physical signal angular probabilities are from the same
analytical formula as the previous pilot, so this is an internal
RECONSTRUCTION test, not independent amplitude validation.
"""
import argparse
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from scalar_threshold_amplitudes import Setup,MW,splitting
from joint_wz_angles import joint_density,azimuthal_cos1_amplitude
from quirkonium_branch_degeneracy import find_low_branch
from mg5_spin_correlated_angles import six_leg_point

def v3(p):
    return (p[1],p[2],p[3])
def dot3(u,v):
    return sum(a*b for a,b in zip(u,v))
def cross(u,v):
    return (u[1]*v[2]-u[2]*v[1],
            u[2]*v[0]-u[0]*v[2],
            u[0]*v[1]-u[1]*v[0])
def unit(v):
    n=math.sqrt(dot3(v,v))
    if n<1.e-12:raise RuntimeError("Degenerate decay-axis basis")
    return tuple(x/n for x in v)
def plus(*rows):
    return [sum(row[i] for row in rows) for i in range(4)]
def boost(p,b):
    """Lorentz boost sending rest-frame p to frame moving at +beta."""
    b2=dot3(b,b)
    if b2>=1:raise ValueError("Superluminal beta")
    if b2<1e-30:return list(p)
    g=1/math.sqrt(1-b2)
    bp=dot3(b,v3(p))
    k=((g-1)*bp/b2+g*p[0])
    return [g*(p[0]+bp),*(p[i+1]+k*b[i] for i in range(3))]
def rest_frame(p,parent):
    return boost(p,tuple(-x/parent[0] for x in parent[1:]))
def decay_axes(n):
    # In the pair CM, beam is global +z for the longitudinal-only boosts
    # used here. Its projection defines a right-handed W helicity frame.
    z=unit(n)
    beam=(0.,0.,1.)
    dp=dot3(beam,z)
    x=unit(tuple(beam[i]-dp*z[i] for i in range(3)))
    y=unit(cross(z,x))
    return z,x,y
def rotation_to_lab(p,theta,azimuth=0.):
    """Map original W +z helicity frame into orientation wrt beam +z."""
    st=math.sin(theta);ct=math.cos(theta)
    ca=math.cos(azimuth);sa=math.sin(azimuth)
    z=(st*ca,st*sa,ct)
    x=(-ct*ca,-ct*sa,st)
    y=(sa,-ca,0.)
    a=v3(p)
    return [p[0],*(a[0]*x[i]+a[1]*y[i]+a[2]*z[i] for i in range(3))]
def lab_event(m,t,cw,cz,phi,theta,rapidity):
    original=six_leg_point(m,t,cw,cz,phi)
    beta=(0.,0.,math.tanh(rapidity))
    return [boost(rotation_to_lab(p,theta),beta) for p in original]

def neutrino_pz_roots(eplus,pnx,pny):
    """Solve on-shell W mass with measured e+ and exact missing pT."""
    pt2=eplus[1]**2+eplus[2]**2
    if pt2<=1e-12:raise RuntimeError("Lepton pT too small for quadratic")
    A=(MW*MW/2+eplus[1]*pnx+eplus[2]*pny)
    disc=A*A-pt2*(pnx*pnx+pny*pny)
    if disc < -1e-7*max(1.,A*A):
        raise RuntimeError("Negative W mass discriminant even with truth MET")
    sqrt_disc=math.sqrt(max(disc,0.))
    roots=[(A*eplus[3]+s*eplus[0]*sqrt_disc)/pt2 for s in (-1,1)]
    return roots

def angle_from_momenta(eplus,nu,muplus,muminus):
    """Reconstruct Phi using charged lepton in W frame, mu- in Z frame."""
    W=plus(eplus,nu);Z=plus(muplus,muminus);X=plus(W,Z)
    Wc=rest_frame(W,X);Zc=rest_frame(Z,X)
    # Wc + Zc are back-to-back in reconstructed pair CM.
    nw,xw,yw=decay_axes(v3(Wc))
    eW=rest_frame(rest_frame(eplus,X),Wc)
    muZ=rest_frame(rest_frame(muminus,X),Zc)
    pW=math.atan2(dot3(v3(eW),yw),dot3(v3(eW),xw))
    pZ=math.atan2(dot3(v3(muZ),yw),-dot3(v3(muZ),xw))
    return (pW+pZ)%(2*math.pi)

def neutrino_from_pz(nux,nuy,nuz):
    return [math.sqrt(nux*nux+nuy*nuy+nuz*nuz),nux,nuy,nuz]

def reco_angles(event,m):
    _,_,eplus,nu,muplus,muminus=event
    nux,nuy=nu[1:3]  # exact MET, no other invisibles.
    roots=neutrino_pz_roots(eplus,nux,nuy)
    true_phi=angle_from_momenta(eplus,nu,muplus,muminus)
    candidates=[]
    for pz in roots:
        guess=neutrino_from_pz(nux,nuy,pz)
        ph=angle_from_momenta(eplus,guess,muplus,muminus)
        X=plus(eplus,guess,muplus,muminus)
        m2=X[0]*X[0]-dot3(v3(X),v3(X))
        mass=math.sqrt(max(0.,m2))
        candidates.append({"pz":pz,"phi":ph,"reconstructed_M":mass})
    minpz=min(candidates,key=lambda c:abs(c["pz"]))
    massmatch=min(candidates,key=lambda c:abs(c["reconstructed_M"]-m))
    exact=min(candidates,key=lambda c:abs(c["pz"]-nu[3]))
    # Both solutions include the correct neutrino pz to floating precision.
    if abs(exact["pz"]-nu[3])>1e-6*max(1,abs(nu[3])):
        raise RuntimeError("True neutrino pz not among quadratic roots")
    return {
        "truth":true_phi,"min_abs_pz":minpz["phi"],
        "known_resonance_mass":massmatch["phi"],
        "equal_roots_cos":sum(math.cos(c["phi"]) for c in candidates)/2,
        "equal_roots_cos2":sum(math.cos(2*c["phi"]) for c in candidates)/2,
        "minpz_is_true":abs(minpz["pz"]-nu[3])<1e-6*max(1,abs(nu[3])),
        "known_mass_is_true":abs(massmatch["pz"]-nu[3])<1e-6*max(1,abs(nu[3])),
    }

def summarize_moments(rows):
    total=sum(w for w,d in rows)
    if total<=0:raise RuntimeError("zero total probability")
    out={}
    for label in ("truth","min_abs_pz","known_resonance_mass","equal_roots"):
        def c1(d):
            return d["equal_roots_cos"] if label=="equal_roots" else math.cos(d[label])
        def c2(d):
            return d["equal_roots_cos2"] if label=="equal_roots" else math.cos(2*d[label])
        a1=2*sum(w*c1(d) for w,d in rows)/total
        a2=2*sum(w*c2(d) for w,d in rows)/total
        out[label]={"a1":a1,"a2":a2,
                    "variance_simple_moment_coefficient":2+a2-a1*a1}
    out["minpz_correct_fraction"]=sum(w*d["minpz_is_true"] for w,d in rows)/total
    out["known_mass_correct_fraction"]=sum(w*d["known_mass_is_true"] for w,d in rows)/total
    out["weight_total"]=total
    return out

def run_one(m,t,nodes,phis,norient,rapidities):
    import numpy as np
    cw,wcw=np.polynomial.legendre.leggauss(nodes)
    cz,wcz=np.polynomial.legendre.leggauss(nodes)
    co,wco=np.polynomial.legendre.leggauss(norient)
    phivecs=[2*math.pi*k/phis for k in range(phis)]
    setup=Setup(m,splitting(m,t),"Z")
    data=[];maxclosure=0.
    for c,wa in zip(cw,wcw):
        for d,wb in zip(cz,wcz):
            for phi in phivecs:
                spinweight=joint_density(setup,float(c),float(d),phi)
                if spinweight<-1e-13:raise RuntimeError("Negative angular density")
                for o,wo in zip(co,wco):
                    theta=math.acos(float(o))
                    for y in rapidities:
                        ev=lab_event(m,t,float(c),float(d),phi,theta,y)
                        obs=reco_angles(ev,m)
                        # Exact truth-pz closure in the SAME helicity convention.
                        closure=abs(math.atan2(math.sin(obs["truth"]-phi),
                                               math.cos(obs["truth"]-phi)))
                        maxclosure=max(maxclosure,closure)
                        if closure>1e-8:raise RuntimeError(
                            f"Truth-angle closure failed: {closure}, phi={phi}")
                        weight=float(wa*wb*wo)*spinweight*(2*math.pi/phis)/(
                            2*len(rapidities))
                        data.append((weight,obs))
    moments=summarize_moments(data)
    moments["tanbeta"]=t
    moments["delta"]=setup.delta
    moments["analytic_closed_a1"]=azimuthal_cos1_amplitude(setup)
    moments["max_truth_angle_closure_radians"]=maxclosure
    moments["n_weighted_points"]=len(data)
    return moments

def sign_cost(b0,b1,label,z):
    x=b0[label];y=b1[label]
    diff=x["a1"]-y["a1"]
    if abs(diff)<1e-12:return math.inf
    # Asymptotic moment estimator for two specified hypotheses,
    # using the worse variance among the two; not full likelihood.
    vari=max(x["variance_simple_moment_coefficient"],
             y["variance_simple_moment_coefficient"])
    return math.ceil(z*z*vari/(diff*diff))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mass",type=float,default=500.)
    p.add_argument("--high-tanbeta",type=float,default=3.)
    p.add_argument("--nodes",type=int,default=5)
    p.add_argument("--phis",type=int,default=12)
    p.add_argument("--orientations",type=int,default=5)
    p.add_argument("--rapidities",default="-1,0,1")
    p.add_argument("--output",type=Path,default=ROOT/
       "validation/local_logs/neutrino_pz_ambiguity_gate.json")
    args=p.parse_args()
    if args.mass<=MW+91.1876 or args.high_tanbeta<=1 or args.nodes<3 or args.phis<8 or args.orientations<3:
        p.error("Invalid kinematic range or angular quadrature")
    rapidities=[float(v) for v in args.rapidities.split(",")]
    if not rapidities or any(abs(y)>4 for y in rapidities):
        p.error("Require comma-separated rapidities with |y| <= 4")
    lo=find_low_branch(args.mass,args.high_tanbeta)
    rows={}
    for label,t in (("low",lo),("high",args.high_tanbeta)):
        rows[label]=run_one(args.mass,t,args.nodes,args.phis,
                            args.orientations,rapidities)
        v=rows[label]
        print(label,"tanbeta",f"{t:.12g}",
              "truth a1",f"{v['truth']['a1']:+.7f}",
              "min|pz| a1",f"{v['min_abs_pz']['a1']:+.7f}",
              "known-M a1",f"{v['known_resonance_mass']['a1']:+.7f}",
              "equal-roots a1",f"{v['equal_roots']['a1']:+.7f}",
              "minpz-truth-fraction",f"{v['minpz_correct_fraction']:.3f}")
    costs={}
    for label in ("truth","min_abs_pz","known_resonance_mass","equal_roots"):
        costs[label]={"3sigma_N":sign_cost(rows["low"],rows["high"],label,3),
                      "5sigma_N":sign_cost(rows["low"],rows["high"],label,5),
                      "signed_difference":rows["low"][label]["a1"]-
                                          rows["high"][label]["a1"]}
    truth=(rows["low"]["truth"]["a1"]>0 and
           rows["high"]["truth"]["a1"]<0)
    r=rows["low"]["min_abs_pz"]["a1"]-rows["high"]["min_abs_pz"]["a1"]
    status=("TOY_SIGN_RETAINED" if truth and r>0 else
            "TOY_SIGN_LOST_OR_REVERSED")
    out={"status":status,"toy_not_a_collider_forecast":True,
         "momenta":"WZ on shell; exact MET; no detector; no backgrounds",
         "resonance_rapidity_distribution":"uniform over explicit test points, NOT pp production",
         "rapidities":rapidities,"nodes":args.nodes,"phis":args.phis,
         "orientations":args.orientations,"M":args.mass,
         "branches":rows,"sign_discrimination_moment_costs":costs,
         "absolute_production_rate":"UNKNOWN",
         "physical_low_tanbeta_model":"UNKNOWN",
         "neutrino_angle_true_root_closure":"PASS",
         "full_fiducial_acceptance":"NOT_EVALUATED"}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2))
    print("STATUS:",status,"ideal model-conditioned reconstruction only; saved",args.output)

if __name__=="__main__":
    main()
