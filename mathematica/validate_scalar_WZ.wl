(* Independent unitary-gauge rank-two amplitude calculation for
   scalar SU(2) doublet annihilation u dbar -> W+V, V=Z or gamma.
   Mathematica 13+: wolframscript -file mathematica/validate_scalar_WZ.wl
   NOT a FeynRules/UFO or arbitrary-Rxi gauge implementation. *)
mw=80379/1000; mz=911876/10000; aw=169/5000;
s=1-mw^2/mz^2; c=1-s; qu=2/3; qd=-1/3;
metric=DiagonalMatrix[{1,-1,-1,-1}];
low[v_]:=metric.v;
outer[a_,b_]:=Outer[Times,low[a],low[b]];
dsplit[m_,t_]:=mw^2/m (1-t^2)/(1+t^2);
tensor[m_,t_,mode_]:=Module[{d,mu,md,mv,ew,ev,p,P,kW,kV,e0,
 gw,gu,gd,gV,du,dd,A},
 d=dsplit[m,t];mu=(m+d)/2;md=(m-d)/2;
 mv=If[mode==="Z",mz,0];
 ew=(m^2+mw^2-mv^2)/(2m);ev=(m^2+mv^2-mw^2)/(2m);
 p=Sqrt[ew^2-mw^2];
 P={m,0,0,0}; kW={ew,0,0,p};kV={ev,0,0,-p};e0={1,0,0,0};
 gw=Sqrt[4Pi aw]/Sqrt[2];
 If[mode==="Z",
 gu=Sqrt[4Pi aw]/Sqrt[c](1/2-s qu);
 gd=Sqrt[4Pi aw]/Sqrt[c](-1/2-s qd);
 gV=Sqrt[4Pi aw]Sqrt[c],
 gu=Sqrt[4Pi aw]Sqrt[s]qu;
 gd=Sqrt[4Pi aw]Sqrt[s]qd;
 gV=Sqrt[4Pi aw]Sqrt[s]];
 du=mv^2-2mu ev;dd=mv^2-2md ev;
 A=gw(gu+gd)metric;
 A+=-gw gu/du outer[d e0-kV,2mu e0-kV];
 A+=gw gd/dd outer[d e0+kV,2md e0-kV];
 A+=-gw gV d/mw^2(
    outer[e0,-P-kW]+(ew-ev)metric+outer[kV+P,e0]);
 <|"A"->A,"W"->kW,"V"->kV,"p"->p,"mV"->mv,"ew"->ew|>
];
amp[m_,t_,mode_]:=Module[{b,A,ex,ey,wl,vl,at,al},
 b=tensor[m,t,mode];A=b["A"];
 ex={0,1,0,0};ey={0,0,1,0};
 at=ex.A.ex;
 If[mode==="gamma",al=0,
 wl={b["p"]/mw,0,0,b["ew"]/mw};
 vl={b["p"]/mz,0,0,-b["V"][[1]]/mz};
 al=wl.A.vl];
 <|"T"->at,"L"->al,"sum"->2at^2+al^2|>
];
(* Published scalar Wgamma / WZ integrated widths: Appendix A.3. *)
reference[m_,t_,mode_]:=Module[{d,D,w,z,b,den,A,F},
 d=dsplit[m,t];D=qu+qd-d/m;
 If[mode==="gamma",
 Return[3aw^2 s/(2m^2)(1-mw^2/m^2)D^2]];
 w=mw^2/m^2;z=mz^2/m^2;b=Sqrt[(1-w-z)^2-4w z];
 den=(1-w-z)^2-(d/m)^2(1+z-w)^2;
 A=((qu+qd)(1-w-z)+c d/(s m)(1+z-w))/den;
 F=(1-d^2/m^2)b^2 A-D(1-w-z);
 3aw^2 s^2/(2c m^2)b(D^2+m^4/(8mw^2 mz^2)F^2)
];
(* Derive Phi Fourier moments from the spin-1 d-matrices by integration. *)
dspin[1,1,x_]:=(1+x)/2;
dspin[0,1,x_]:=Sqrt[1-x^2]/Sqrt[2];
dspin[-1,1,x_]:=(1-x)/2;
dspin[1,-1,x_]:=(1-x)/2;
dspin[0,-1,x_]:=-Sqrt[1-x^2]/Sqrt[2];
dspin[-1,-1,x_]:=(1+x)/2;
iw[i_,j_]:=iw[i,j]=Integrate[dspin[i,1,x]dspin[j,1,x],{x,-1,1}];
iz[i_,j_]:=iz[i,j]=FullSimplify[(
 s^2 iw[i,j]+(-1/2+s)^2
 Integrate[dspin[i,-1,x]dspin[j,-1,x],{x,-1,1}])/
 (s^2+(-1/2+s)^2)];
angleCoeff[B_,n_]:=Module[{hs={-1,0,1},h,norm},
 h=<|-1->-B["T"],0->B["L"],1->-B["T"]|>;
 norm=Total[Table[h[k]^2 iw[k,k]iz[k,k],{k,hs}]];
 2Total[Flatten[Table[If[i-j==n,h[i]h[j]iw[i,j]iz[i,j],0],
 {i,hs},{j,hs}]]]/norm
];
passed=True;tol=10^-22;
Do[
 b=tensor[m,t,mode];A=amp[m,t,mode];
 beta=Sqrt[(1-mw^2/m^2-b["mV"]^2/m^2)^2-
  4mw^2 b["mV"]^2/m^4];
 computed=3/(32Pi^2 m^2)beta A["sum"];
 residual=Abs[N[computed/reference[m,t,mode]-1,35]];
 If[residual>=tol,Print["FAIL width ",m,t,mode,residual];passed=False];
 If[mode==="gamma",
  ex={0,1,0,0};
  wl={b["p"]/mw,0,0,b["ew"]/mw};
  ward=Max[Abs[N[ex.b["A"].b["V"],35]],
           Abs[N[wl.b["A"].b["V"],35]]];
  If[ward>=tol,Print["FAIL Ward ",m,t,ward];passed=False],
  f0=N[A["L"]^2/A["sum"],16];
  Print["M=",m," tanbeta=",t," f00=",f0,
    " a1=",N[angleCoeff[A,1],12],
    " a2=",N[angleCoeff[A,2],12]]
 ],
 {m,{250,500,1000}},{t,{1,3,10}},{mode,{"Z","gamma"}}];
If[passed,Print["PASS Mathematica tensor / published rates / Ward"],
 Print["FAIL Mathematica"];Exit[1]];
Exit[0];
