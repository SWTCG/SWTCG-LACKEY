# SWTCG Card Cost Reference

Generated from 8998 cards (excluding Subordinates).

Model: Ridge regression with 5-fold CV alpha selection. Interaction terms (power x keyword) added for Accuracy, Critical Hit, Fury.

---


## Space (1461 cards)

**Regression model** (Ridge) — n=1452, R^2=0.897, RMSE=0.89, alpha=3.665

```
Predictor                      Coeff
-------------------------------------
Constant                       0.640
power                          0.332
health                         0.642
Shields                        0.254
Accuracy                       0.510
Critical Hit                   0.211
Deploy                         0.399
Armor                          0.382
Evade                          0.113
Bombard                        0.002
Hidden Cost                    0.274
Intercept                      0.159
Alternative Cost              -0.105
Stealth                        0.430
Overkill                       0.301
Lucky                          0.096
Upkeep                        -0.496
Pilot                          0.194
Bounty                        -0.077
Stun                           0.037
Retaliate                      0.087
Precision                      0.240
Damage Control                 0.214
Stack                          0.043
Velocity                      -0.026
Absorb                         0.167
Reserves                       0.288
Double Strike                  0.757
Reduced Cost                  -0.039
Resilience                     0.195
Fury                           0.418
Ambush                        -0.022
Focus                          0.023
Inspiration                    1.244
Protect                        0.069
Double Damage                  0.450
Ferocity                       0.433
Ion Cannon                     0.096
Deflect                        0.142
Redirect                       0.309
Parry                          0.173
Riposte                        0.006
Surge                          0.020
Area Damage                    0.147
Backfire                      -0.089
Switch                         0.154
Accuracy (x power)            -0.005
Critical Hit (x power)        -0.013
Fury (x power)                -0.043
freeform_count                 0.178
army_count                     0.166
prevention_ceiling             0.148
prevention_force_cost          0.021
protect_ceiling                0.069
protect_force_cost            -0.028
retaliate_ceiling              0.087
retaliate_force_cost          -0.286
ambush_ceiling                -0.022
ambush_force_cost              0.211
is_unique                      0.264
multi_arena                    0.358
```

_Note: Ridge coefficients are regularized toward zero. Interaction terms (power x keyword) capture scaling effects._

**Cost curve:**

```
Cost |    N | Avg P | Avg H | Avg P+H | P range | H range
----------------------------------------------------------
   1 |    8 |   0.9 |   1.0 |     1.9 | 0-2    | 1-1
   2 |   31 |   1.5 |   1.5 |     3.0 | 0-2    | 1-3
   3 |  136 |   2.4 |   2.6 |     5.0 | 0-6    | 1-6
   4 |  212 |   2.8 |   3.4 |     6.2 | 0-6    | 1-7
   5 |  272 |   3.4 |   4.1 |     7.5 | 0-6    | 2-10
   6 |  254 |   4.2 |   5.1 |     9.3 | 0-8    | 3-10
   7 |  192 |   4.9 |   5.6 |    10.6 | 0-10   | 2-10
   8 |  130 |   5.6 |   6.5 |    12.1 | 0-8    | 4-10
   9 |   55 |   6.9 |   7.3 |    14.3 | 4-9    | 4-10
  10 |   61 |   7.2 |   8.8 |    15.9 | 0-11   | 6-12
  11 |   30 |   8.0 |   9.1 |    17.1 | 5-10   | 7-12
  12 |   25 |   9.4 |   9.9 |    19.3 | 0-15   | 7-14
  13 |    7 |  10.1 |  10.7 |    20.9 | 7-14   | 10-14
  14 |   16 |  11.2 |  11.6 |    22.9 | 0-16   | 8-20
  15 |    6 |  10.2 |  13.8 |    24.0 | 0-15   | 12-18
  16 |    9 |  13.8 |  13.2 |    27.0 | 9-16   | 9-16
  17 |    2 |   7.0 |  17.5 |    24.5 | 0-14   | 15-20
  18 |    2 |  16.0 |  17.5 |    33.5 | 12-20   | 15-20
  20 |    2 |  20.0 |  20.0 |    40.0 | 20-20   | 20-20
```

**Keyword frequency by cost tier:**

```
Cost  1: Velocity (12%), Meditate (12%), Ferocity (12%), Backfire (12%), Bounty (12%)
Cost  2: Stealth (6%), Velocity (6%), Intercept (6%), Accuracy (6%), Reserves (6%)
Cost  3: Critical Hit (18%), Shields (10%), Alternative Cost (9%), Intercept (8%), Accuracy (7%)
Cost  4: Shields (15%), Accuracy (11%), Critical Hit (10%), Evade (9%), Deploy (9%)
Cost  5: Shields (18%), Critical Hit (14%), Accuracy (14%), Evade (13%), Deploy (9%)
Cost  6: Shields (25%), Accuracy (15%), Armor (11%), Critical Hit (11%), Deploy (10%)
Cost  7: Shields (29%), Critical Hit (16%), Accuracy (15%), Armor (12%), Bombard (11%)
Cost  8: Shields (27%), Critical Hit (16%), Accuracy (14%), Evade (13%), Bombard (12%)
Cost  9: Shields (38%), Armor (33%), Accuracy (22%), Deploy (16%), Overkill (11%)
Cost 10: Shields (33%), Hidden Cost (23%), Armor (18%), Deploy (18%), Overkill (15%)
Cost 11: Shields (33%), Overkill (23%), Deploy (23%), Armor (17%), Hidden Cost (17%)
Cost 12: Deploy (42%), Shields (27%), Critical Hit (23%), Overkill (19%), Bombard (19%)
Cost 13: Shields (29%), Accuracy (29%), Armor (29%), Bombard (14%), Ferocity (14%)
Cost 14: Stack (44%), Shields (38%), Redirect (25%), Retaliate (19%), Upkeep (12%)
Cost 15: Ion Cannon (67%), Hidden Cost (67%), Absorb (67%), Ferocity (33%), Fortitude (33%)
Cost 16: Overkill (56%), Shields (44%), Evade (22%), Damage Control (22%), Inspiration (22%)
```

**Stat-weak cards** (P+H > 1.5 SD below cost-tier mean -- likely have significant abilities):

```
Cost  4: Spacetrooper [ER]  P=0, H=2 (mean P+H=6.2)
         "Switch: +1 health/+2 power, Ion Cannon 2 | Armor | As long as this unit is in th..."
Cost  4: General Leia Organa Solo (K2) [15TH]  P=0, H=3 (mean P+H=6.2)
         "Switch: Damage Control 2/+2 power, Lucky 2 | Leia doesn't count toward controlli..."
Cost  4: Meditation Sphere [SITH]  P=1, H=2 (mean P+H=6.2)
         "Reserves: [tap], Pay 1 Force -> Prevent 1 damage to one of your Dark Jedi or Sit..."
Cost  4: Tyranus's Solar Sailer (A) [AOTC]  P=2, H=2 (mean P+H=6.2)
         "Critical Hit 2 | When its attack ends, you may retreat Tyranus's Solar Sailer."
Cost  4: Scarif TIE Striker [BF]  P=2, H=2 (mean P+H=6.2)
         "Switch: Avenge 2/Area Damage 2 (Whenever damage from this unit's attack causes a..."
Cost  4: Virago (B) [BH]  P=0, H=4 (mean P+H=6.2)
         "Armor | Whenever Virago attacks, you may a die. If you do, and roll a 1) Your op..."
Cost  4: Finn's Shuttle (B) [BOC]  P=1, H=3 (mean P+H=6.2)
         "Reduced Cost 3: If Finn is in any arena. | Resilience 2 | When Finn's Shuttle is..."
Cost  4: Rebel X-Wing [BOH] [BANNED]  P=2, H=2 (mean P+H=6.2)
         "Switch: Double Strike/+1 power, Stun 2 | Fury 2"
Cost  4: TIE Fighter DS-55-2 [BOY]  P=2, H=2 (mean P+H=6.2)
         "Accuracy 1 | Pay 1 Force -> Intercept"
Cost  4: ARC-170 [CAD]  P=2, H=2 (mean P+H=6.2)
         "Double Damage (Double the damage, after damage prevention, done by this unit.) |..."
Cost  4: Invading Tri-Fighter [CWSO]  P=3, H=1 (mean P+H=6.2)
         "Treat this unit as a Separatist | Switch: Accuracy 1/Critical Hit 1 | Accuracy 1"
Cost  4: ARC Fighter [FOTR]  P=2, H=2 (mean P+H=6.2)
         "This unit can have up to 2 extra Pilots. | This unit can't have more than 4 Pilo..."
Cost  4: Jehavey'ir-Type Assault Ship [MAND]  P=2, H=2 (mean P+H=6.2)
         "This unit gets +1 power and +1 health for each 10 cards in your opponent's disca..."
Cost  4: Jedi Recruitment Transport [RO2]  P=1, H=3 (mean P+H=6.2)
         "Tap -> Search your deck for up to 3 Force Sensitive Child unit cards, show them ..."
Cost  4: Gray Squadron Y-Wing [ROTJ]  P=2, H=2 (mean P+H=6.2)
         "Armor | Stun 2"
Cost  4: Rogue Eight (A) [RS]  P=2, H=2 (mean P+H=6.2)
         "As long as Nawara Ven is piloting Rogue Eight, it gets Accuracy 1. | Each of you..."
Cost  4: Rogue Eleven (A) [RS]  P=2, H=2 (mean P+H=6.2)
         "Each of your other Rogue Starfighters gets "Pay 1 Force -> Deflect 1.""
Cost  4: Rogue Seven (A) [RS]  P=2, H=2 (mean P+H=6.2)
         "Switch: +1 health/+1 power | Each of your other Rogue Starfighters gets "Pay 0 F..."
Cost  4: Sh'rip Sh'pa [TUF]  P=0, H=4 (mean P+H=6.2)
         "Tap -> Add X+1 counters to your Resource, where X is the number of Locations you..."
Cost  5: Grievous's Starfighter (C) [CAD]  P=0, H=3 (mean P+H=7.5)
         "Switch: +3 power, Accuracy 1/Stealth | Discard a card from your hand -> Search y..."
Cost  5: Vader's TIE Fighter (A) [ANH]  P=3, H=2 (mean P+H=7.5)
         "Pay 2 Force -> Evade 2 | When Vader's TIE Fighter is discarded from the Characte..."
Cost  5: X-Wing Red One [ANH]  P=3, H=2 (mean P+H=7.5)
         "When this unit attacks, you may give it +3 power for that attack. If you do, thi..."
Cost  5: Sidious's Shuttle (A) [BL]  P=3, H=2 (mean P+H=7.5)
         "Shields 1 | When you deploy Sidious's Shuttle, you may search your deck for a Da..."
Cost  5: Yoda's Starfighter (A) [BL]  P=2, H=3 (mean P+H=7.5)
         "When deploy Yoda's Starfighter you do, your deck for a Yoda unit card search you..."
Cost  5: Yoda's Starfighter (A) (Promo) [BL]  P=2, H=3 (mean P+H=7.5)
         "When deploy Yoda's Starfighter you do, your deck for a Yoda unit card search you..."
Cost  5: ARC Support Fighter [CAD]  P=3, H=2 (mean P+H=7.5)
         "This unit gets Accuracy 2 when attacking a Jedi. | Pay 0 Force -> Intercept"
Cost  5: A-Class BFF-1 Cargo Carrier [ER]  P=0, H=5 (mean P+H=7.5)
         "Tap -> Gain 1 build point. Play only during your build step. | Tap -> Draw a car..."
Cost  5: Tyranus's Solar Sailer (B) [JG]  P=3, H=2 (mean P+H=7.5)
         "Reserves: Tap, Pay 4 Force -> Prevent 1 damage to one of your units in the Chara..."
Cost  5: Star Commuter Shuttle [SOR]  P=0, H=5 (mean P+H=7.5)
         "As long as you have a Location in the Space or Ground arena, this unit gets "Tap..."
Cost  5: Naga's Meditation Sphere (A) [TAL]  P=1, H=4 (mean P+H=7.5)
         "Reserves: Tap -> Gain 2 Forc.e | Reserves: Tap, Pay 4 Force -> Take 1 Subordinat..."
Cost  6: Slave Divers [DAN]  P=0, H=4 (mean P+H=9.3)
         "This unit costs 1 less build counter to deploy for each Slave you have in any ar..."
Cost  6: Big Asteroid [RAS]  P=1, H=3 (mean P+H=9.3)
         "Big Asteroid doesn't count toward controlling the Space arena. | When this unit ..."
Cost  6: Poe's Starfighter (F) [BAE]  P=3, H=3 (mean P+H=9.3)
         "Switch: Shields 1/Velocity 10 | Accuracy 1 | Each of your opponent's units in th..."
Cost  6: Crucible (A) [BL]  P=1, H=5 (mean P+H=9.3)
         "Tap -> Search your deck for a Force Sensitive or Jedi Padawan unit card, show it..."
Cost  6: Blue Three (B) [BOSB]  P=3, H=3 (mean P+H=9.3)
         "Switch: Accuracy 1/Double Damage | When you deploy Blue Three, you may search yo..."
Cost  6: Poe's Starfighter (C) [BOSB]  P=3, H=3 (mean P+H=9.3)
         "Switch:  Accuracy 1/Inspiration | As long as Poe's Starfighter has a Pilot, each..."
Cost  6: Red Four (B) [BOSB]  P=3, H=3 (mean P+H=9.3)
         "Switch: Focus 1/Double Strike | When you deploy Red Four, you may remove 1 damag..."
Cost  6: A-Class Bulk Freighter [ER]  P=0, H=6 (mean P+H=9.3)
         "Tap -> Take 1 50/2/2 Imperial Starfighter Subordinate and put it beneath this un..."
Cost  6: Jedi Transport [PM]  P=3, H=3 (mean P+H=9.3)
         "Shields 1 | Pay 1 Force -> Evade 1 | When this unit is discarded from the Space ..."
Cost  6: GR-75 Medium Transport [RS]  P=1, H=5 (mean P+H=9.3)
         "Switch: Lucky 1/Shields 1 | Tap -> Gain 2 build points. Play only during your bu..."
Cost  6: TIE Bomber Squadron  [RS]  P=3, H=3 (mean P+H=9.3)
         "Switch:  Bombard 3/+2 power | Hidden Cost 4 | As long as you have an Imperial Of..."
Cost  6: Blue Three (A) [TFA]  P=3, H=3 (mean P+H=9.3)
         "Accuracy 1 | Double Damage | Lucky 1 | As long as Blue Three is piloted by Jessi..."
Cost  6: Kylo's TIE Silencer (A) [TLJ]  P=3, H=3 (mean P+H=9.3)
         "Alternative Cost: Pay 2 build points, pay 2 Force, tap Supremacy. | As long as S..."
Cost  6: Kylo's TIE Silencer (A) (Promo) [TLJ]  P=3, H=3 (mean P+H=9.3)
         "Alternative Cost: Pay 2 build points, pay 2 Force, tap Supremacy. | As long as S..."
Cost  6: Jaina's X-wing (C) [VP]  P=3, H=3 (mean P+H=9.3)
         "Precision | Jaina's X-wing gets +2 power when attacking a Capital Ship, Fleet, o..."
Cost  6: Jedi Academy Transport [VP]  P=2, H=4 (mean P+H=9.3)
         "When you deploy this unit, you may choose one of your Characters. If you do, the..."
Cost  7: Jaina's X-Wing (D) [SBS]  P=3, H=2 (mean P+H=10.6)
         "Hidden Cost 5 | Accuracy 1 | Critical Hit 1 | Precision | Lucky 1 | Shields 1 | ..."
Cost  7: Sw-0608 (B) [RO]  P=2, H=4 (mean P+H=10.6)
         "Switch: Stealth/Damage Control 1 | SW-0608 can have up to 2 Pilots. | When you d..."
Cost  7: Vader's Interceptor (A) [TDT]  P=3, H=3 (mean P+H=10.6)
         "Stack: Vader's TIE Fighter | Accuracy 2 | Inspiration | Pay 2 Force -> Evade 3"
Cost  7: Vader's Interceptor (B) [TDT]  P=3, H=3 (mean P+H=10.6)
         "Hidden Cost 4 | Double Strike | Pay 1 Force -> Evade 2 | INSERT: Pay 1 Force -> ..."
Cost  7: Poe's Starfighter (B) [TFA]  P=3, H=3 (mean P+H=10.6)
         "Switch:+10 speed/+1 power | Accuracy 2 | Double Strike"
Cost  7: Heart of  Artorias (B) [VP]  P=3, H=3 (mean P+H=10.6)
         "Heart of Artorias gets +1 power and +1 health for each Refugee in any arena."
Cost  7: Kaliida Shoals Medical Center (A) [AGD]  P=0, H=7 (mean P+H=10.6)
         "When Kaliida Shoals Medical Center is discarded from the Space arena, put 2 dama..."
Cost  7: Last Resort (A) [DAN]  P=2, H=5 (mean P+H=10.6)
         "Lucky 2 | When the Space battle step starts, you may choose one of your Transpor..."
Cost  7: SW-0608 (A) [RO]  P=3, H=4 (mean P+H=10.6)
         "Sw-0608 can have up to 2 Pilots. | Stealth | When you deploy SW-0608, you may se..."
Cost  7: TIE Striker Squadron [RO]  P=3, H=4 (mean P+H=10.6)
         "Switch: +1 health/+10 speed, Fury 1 | Precision | Double Strike | Pay 2 Force ->..."
Cost  7: Prism (A) [TDT]  P=0, H=7 (mean P+H=10.6)
         "When your build step starts, you may choose one of your opponent's units with mo..."
Cost  7: TIE Fighter Construction Facility [TDT]  P=0, H=7 (mean P+H=10.6)
         "When you deploy this unit, take 3 60/1/1 Imperial TIE Fighter Subordinates and p..."
Cost  8: Asajj's Starfighter (C) [AGD]  P=3, H=4 (mean P+H=12.1)
         "Fury 2 | Inspiration | Pay 1 Force -> Evade 2"
Cost  8: Millennium Falcon (B2) [BOC]  P=3, H=5 (mean P+H=12.1)
         "Switch: +2 power/Double Strike | The Millennium Falcon gets Critical Hit 2 when ..."
Cost  8: Slave I (C) [JG]  P=4, H=4 (mean P+H=12.1)
         "Slave I gets +2 power as long as it's attacking a Jedi. Accuracy 2 (Add +2 to ea..."
Cost  8: Twin Suns Squadron (D) [LEG]  P=4, H=4 (mean P+H=12.1)
         "Twin Suns Squadron can only be piloted by a Jedi. | Accuracy 2 | Shields 1 | Pay..."
Cost  8: Twin Suns Squadron (D) (Promo) [LEG]  P=4, H=4 (mean P+H=12.1)
         "Twin Suns Squadron can only be piloted by a Jedi. | Accuracy 2 | Shields 1 | Pay..."
Cost  8: ISO-L8 (A) [TDT]  P=0, H=8 (mean P+H=12.1)
         "When our build step starts, you may choose one of your opponent's units with mor..."
Cost  9: A-vek Liluunu-Class Carrier [VP]  P=4, H=5 (mean P+H=14.3)
         "When you deploy this unit, take 2 50/3/2 Coralskipper Subordinates with "Shields..."
Cost  9: Millennium Falcon (A2) [BOC]  P=6, H=4 (mean P+H=14.3)
         "Switch: Bombard 4/Accuracy 1 | Hidden Cost 6 | Whenever damage from the Millenni..."
Cost  9: Millennium Falcon (A2) (Promo) [BOC]  P=6, H=4 (mean P+H=14.3)
         "Switch: Bombard 4/Accuracy 1 | Hidden Cost 6 | Whenever damage from the Millenni..."
Cost 10: Galaxy Gun (A) [EE]  P=0, H=8 (mean P+H=15.9)
         "Tap -> Roll a die. If you roll a 5 or 6, discard each of your opponent's units i..."
Cost 10: Refugee Convoy [VP]  P=3, H=6 (mean P+H=15.9)
         "This unit costs 1 less build counter to deploy for each Refugee in any arena. | ..."
Cost 10: Fury Station (A) [TAL]  P=0, H=10 (mean P+H=15.9)
         "Upkeep: Put 1 damage counter on Fury Station or return it to your hand. | As lon..."
Cost 10: Chimaera (E) [FOR]  P=4, H=8 (mean P+H=15.9)
         "Armor | Lucky 2 | Double Strike | Pay 3 build point -> Take 1 70/3/3 Imperial TI..."
Cost 10: Black Eight Squadron (A) [TDT]  P=6, H=6 (mean P+H=15.9)
         "Accuracy 2 | Elude | As long as you have Darth Vader in any arena, Black Eight S..."
Cost 11: Gemini-class Star Destroyer [VV1]  P=6, H=7 (mean P+H=17.1)
         "Deploy: Take 1 Gemini-class Star Destroyer from outside the game and put it into..."
Cost 11: Gemini-class Star Destroyer (Promo) [VV1]  P=6, H=7 (mean P+H=17.1)
         "Deploy: Take 1 Gemini-class Star Destroyer from outside the game and put it into..."
Cost 12: Death Star (D) [TDT]  P=0, H=12 (mean P+H=19.3)
         "When you deploy the Death Star, you may search your deck or discard pile for up ..."
Cost 12: Death Star (D) (Promo) [TDT]  P=0, H=12 (mean P+H=19.3)
         "When you deploy the Death Star, you may search your deck or discard pile for up ..."
Cost 14: Abeloth (A) [15TH]  P=9, H=9 (mean P+H=22.9)
         "Stack: Any unique unit with "Force in its game text or subtype. | Upkeep: Gain 1..."
Cost 15: Exis Station (A) [TAL]  P=0, H=18 (mean P+H=24.0)
         "Upkeep:Put 1 damage counter on Exis Station. | Shields 1 | Whenever one of your ..."
```


## Ground (1995 cards)

**Regression model** (Ridge) — n=1970, R^2=0.855, RMSE=0.95, alpha=3.665

```
Predictor                      Coeff
-------------------------------------
Constant                       0.354
power                          0.336
health                         0.663
Armor                          0.393
Critical Hit                  -0.029
Accuracy                       0.562
Evade                          0.004
Stack                         -0.046
Deploy                         0.110
Fury                          -0.020
Hidden Cost                    0.296
Bounty                        -0.146
Stealth                        0.357
Retaliate                      0.107
Lucky                         -0.024
Shields                        0.282
Intercept                     -0.051
Damage Control                 0.089
Double Strike                  0.575
Alternative Cost              -0.130
Upkeep                        -0.338
Overkill                       0.490
Parry                          0.097
Absorb                         0.064
Protect                       -0.016
Deflect                        0.351
Focus                          0.025
Stun                           0.215
Ambush                         0.035
Reduced Cost                  -0.072
Reserves                       0.141
Ion Cannon                     0.049
Velocity                      -0.013
Resilience                     0.082
Foresight                      0.133
Precision                      0.155
Area Damage                    0.175
Pilot                         -0.215
Ferocity                       0.663
Riposte                        0.195
Double Damage                  0.700
Switch                         0.568
Inspiration                    1.226
Backfire                      -0.093
Redirect                      -0.024
Persuade                      -0.278
Surge                         -0.110
Accuracy (x power)            -0.048
Critical Hit (x power)         0.053
Fury (x power)                 0.032
freeform_count                 0.178
army_count                     0.072
prevention_ceiling             0.141
prevention_force_cost          0.050
protect_ceiling               -0.016
protect_force_cost             0.003
retaliate_ceiling              0.107
retaliate_force_cost          -0.341
ambush_ceiling                 0.035
ambush_force_cost              0.215
is_unique                      0.495
multi_arena                    0.540
```

_Note: Ridge coefficients are regularized toward zero. Interaction terms (power x keyword) capture scaling effects._

**Cost curve:**

```
Cost |    N | Avg P | Avg H | Avg P+H | P range | H range
----------------------------------------------------------
   1 |    3 |   1.0 |   1.7 |     2.7 | 0-2    | 1-3
   2 |   66 |   1.6 |   2.1 |     3.7 | 0-4    | 1-4
   3 |  210 |   2.2 |   2.9 |     5.1 | 0-6    | 1-6
   4 |  347 |   2.8 |   3.7 |     6.5 | 0-7    | 1-8
   5 |  319 |   3.5 |   4.4 |     7.9 | 0-6    | 1-10
   6 |  354 |   4.5 |   4.9 |     9.4 | 0-7    | 1-10
   7 |  235 |   5.0 |   5.6 |    10.6 | 0-9    | 3-9
   8 |  190 |   5.6 |   6.0 |    11.6 | 0-10   | 4-12
   9 |   95 |   6.4 |   6.6 |    12.9 | 0-10   | 4-12
  10 |   58 |   7.2 |   8.1 |    15.4 | 0-13   | 5-15
  11 |   36 |   8.0 |   8.3 |    16.3 | 4-12   | 5-12
  12 |   24 |   8.4 |   8.6 |    17.0 | 0-12   | 7-12
  13 |   10 |   6.8 |  10.3 |    17.1 | 0-10   | 8-14
  14 |    8 |  10.8 |   9.9 |    20.6 | 9-15   | 8-12
  15 |    7 |  10.4 |  11.7 |    22.1 | 8-12   | 10-13
  19 |    4 |   0.0 |  20.0 |    20.0 | 0-0    | 20-20
  20 |    2 |  20.0 |  20.0 |    40.0 | 20-20   | 20-20
```

**Keyword frequency by cost tier:**

```
Cost  2: Accuracy (15%), Alternative Cost (9%), Reserves (9%), Lucky (8%), Pilot (6%)
Cost  3: Critical Hit (9%), Deploy (9%), Accuracy (8%), Reserves (8%), Reduced Cost (5%)
Cost  4: Deploy (10%), Critical Hit (10%), Armor (10%), Accuracy (9%), Fury (6%)
Cost  5: Critical Hit (12%), Accuracy (11%), Armor (11%), Evade (10%), Deploy (9%)
Cost  6: Stack (17%), Evade (14%), Armor (14%), Critical Hit (13%), Accuracy (13%)
Cost  7: Accuracy (18%), Armor (16%), Stack (16%), Critical Hit (14%), Evade (12%)
Cost  8: Stack (22%), Armor (20%), Critical Hit (19%), Evade (15%), Hidden Cost (10%)
Cost  9: Armor (27%), Evade (23%), Accuracy (18%), Stack (16%), Critical Hit (14%)
Cost 10: Armor (29%), Overkill (26%), Stack (19%), Evade (17%), Absorb (12%)
Cost 11: Accuracy (29%), Evade (24%), Deflect (21%), Stack (21%), Armor (16%)
Cost 12: Deploy (29%), Armor (29%), Area Damage (17%), Critical Hit (17%), Evade (12%)
Cost 13: Velocity (33%), Ferocity (33%), Ion Cannon (25%), Overkill (25%), Stun (17%)
Cost 14: Accuracy (38%), Critical Hit (38%), Parry (25%), Fury (25%), Retaliate (25%)
Cost 15: Ion Cannon (57%), Hidden Cost (57%), Absorb (57%), Deploy (43%), Ferocity (29%)
```

**Stat-weak cards** (P+H > 1.5 SD below cost-tier mean -- likely have significant abilities):

```
Cost  2: Binding Energy [ALTA]  P=0, H=2 (mean P+H=3.7)
         "You may stack this card beneath any unit, and there can only be one copy of this..."
Cost  2: Zam's Airspeeder (A) [AOTC]  P=1, H=1 (mean P+H=3.7)
         "Critical Hit 3"
Cost  2: Bogwing [ESB]  P=1, H=1 (mean P+H=3.7)
         "[tap] -> Choose a player. That player discards the top 2 cards of his or her dec..."
Cost  2: Single Trooper Aerial Platform [ION]  P=1, H=1 (mean P+H=3.7)
         "This unit gets +1 power for each Trade Federation Speeder in the Ground arena."
Cost  2: Gondola Speeder [JG]  P=1, H=1 (mean P+H=3.7)
         "Tap -> Move one of your Characters from the Space arena into the Character arena..."
Cost  2: Gizka [KAE]  P=1, H=1 (mean P+H=3.7)
         "Reduced Cost 1: If a Gizka is in any arena. | Tap -> One of your opponent's Grou..."
Cost  2: Jedi Scout Speeder [LEG]  P=1, H=1 (mean P+H=3.7)
         "Accuracy 1 | Critical Hit 1 | Pay 1 Force -> Evade 2"
Cost  2: Zam's Airspeeder (C) [SAV]  P=1, H=1 (mean P+H=3.7)
         "Discard Zam's Airspeeder from the Ground arena -> Choose one of your Bounty Hunt..."
Cost  2: Zam's Airspeeder (C) (LEGO) [SAV]  P=1, H=1 (mean P+H=3.7)
         "Discard Zam's Airspeeder from the Ground arena -> Choose one of your Bounty Hunt..."
Cost  3: Battle Droid Marine [CWSO]  P=1, H=1 (mean P+H=5.1)
         "Switch: +1 power / +1 health | Whenever this unit would take 2 or less damage, i..."
Cost  3: Bespin Engineers [SAV]  P=1, H=1 (mean P+H=5.1)
         "Reserves: [tap], Pay 1 Force -> Choose one of your units with Upkeep. You do not..."
Cost  3: Jedi Padawan Squad [AGD]  P=1, H=2 (mean P+H=5.1)
         "As long as Ahsoka Tano is in any arena, this unit gets +30 speed. | This unit ge..."
Cost  3: Porg Flock [ALTA]  P=0, H=3 (mean P+H=5.1)
         "When you deploy this unit, take 1 20/1/1 Curious Porg Subordinate and put it int..."
Cost  3: Death Star Cannon Tower [ANH]  P=0, H=3 (mean P+H=5.1)
         "Ion Cannon 3"
Cost  3: Ewok Villagers [BOE]  P=1, H=2 (mean P+H=5.1)
         "Reserves: [tap] -> One of your attacking Ewoks gets +3 power for this attack. If..."
Cost  3: Coruscant Cleaning Droids [CAD]  P=1, H=2 (mean P+H=5.1)
         "When you deploy this unit, you may reveal a partially built Location card in you..."
Cost  3: Loth-bat [FOR]  P=0, H=3 (mean P+H=5.1)
         "Alternative Cost: Tap one of your Lothal Units. | [Tap] -> Each of your other Lo..."
Cost  3: Tyranus's Geonosian Speeder (B) [JG]  P=2, H=1 (mean P+H=5.1)
         "When one of your opponent's units attacks this unit, you may search your deck. Y..."
Cost  3: Imperial Scientists [RO]  P=0, H=3 (mean P+H=5.1)
         "When this unit is discarded from the Ground arena, you may reveal a partially bu..."
Cost  3: Savareen Decoy Team [SOLO]  P=0, H=3 (mean P+H=5.1)
         "Treat this unit as a Rebel Pirate. | Ion Cannon 3 | Tap -> One of your units get..."
Cost  3: Jedi Youngling Survivors [TDT]  P=1, H=2 (mean P+H=5.1)
         "As long as you have a Jedi Master in any arena, whenever a unit attacks this uni..."
Cost  3: Nosaurian Slaves [TDT]  P=0, H=3 (mean P+H=5.1)
         "When you deploy this unit, you may discard X cards from your hand. If you do, pu..."
Cost  3: Luke's X-Wing (F) [TLJ]  P=0, H=3 (mean P+H=5.1)
         "When Luke's X-Wing is discarded from the Ground arena, gain 1 Force. | Tap -> Ch..."
Cost  3: Peli's Pit Droids (A) [TM]  P=0, H=3 (mean P+H=5.1)
         "Your opponent must pay 2 Force to attack Peli's Pit Droids. | Tap -> Remove up t..."
Cost  3: Farming R6 Droids [TM]  P=0, H=3 (mean P+H=5.1)
         "Alternative Cost: Tap one of your Farmers in any arena. | Tap -> Take 2 30/0/2 B..."
Cost  3: Stormtrooper Mortar Specialist [TMW]  P=0, H=3 (mean P+H=5.1)
         "Precision | [tap] -> Choose the Ground or Character arena. Then choose one of yo..."
Cost  3: Sea Skiff [TROS]  P=0, H=3 (mean P+H=5.1)
         "Reduced Cost 2: If an Aquatic Location is in the Ground or Character arena. | Ta..."
Cost  3: Refugees [VP]  P=0, H=3 (mean P+H=5.1)
         "Tap -> Add 1 counter to your Resource. Play only during your build step and only..."
Cost  4: Scared Porg Flock [TLJ]  P=0, H=3 (mean P+H=6.5)
         "Whenever this unit would be damaged, prevent up to 2 of that damage. | As long a..."
Cost  4: Fodesinbeed Annodue (A) [BEP]  P=2, H=2 (mean P+H=6.5)
         "Reduced Cost 3: If a Podracer is in any arena. | Whenever you move a Pilot to a ..."
Cost  4: Scarif TIE Striker [BF]  P=2, H=2 (mean P+H=6.5)
         "Switch: Avenge 2/Area Damage 2 (Whenever damage from this unit's attack causes a..."
Cost  4: Getaway Speeder [BH]  P=0, H=4 (mean P+H=6.5)
         "Reserves: [tap], Put 1 damage counter on this unit -> Retreat one of your Bounty..."
Cost  4: Finn's Shuttle (B) [BOC]  P=1, H=3 (mean P+H=6.5)
         "Reduced Cost 3: If Finn is in any arena. | Resilience 2 | When Finn's Shuttle is..."
Cost  4: Finn's Ski Speeder (C) [BOC]  P=1, H=3 (mean P+H=6.5)
         "Put 1 damage counter on Finn's Ski Speeder -> Put 3 damage counters on one of yo..."
Cost  4: Rebel X-Wing [BOH] [BANNED]  P=2, H=2 (mean P+H=6.5)
         "Switch: Double Strike/+1 power, Stun 2 | Fury 2"
Cost  4: Thundering Herd AT-PT [BOH]  P=2, H=2 (mean P+H=6.5)
         "Armor | Double Strike | Whenever your opponent deploys a unit to the Ground aren..."
Cost  4: Imperial Dewback [BOY]  P=2, H=2 (mean P+H=6.5)
         "This unit gets +4 power as long as it's attacking a neutral unit. | Accuracy 1"
Cost  4: Siphon Generator [CWSO]  P=0, H=4 (mean P+H=6.5)
         "Tap -> Gain 1 Force for each Location in play and do 1 damage to each unit in th..."
Cost  4: Invading Tri-Fighter [CWSO]  P=3, H=1 (mean P+H=6.5)
         "Treat this unit as a Separatist | Switch: Accuracy 1/Critical Hit 1 | Accuracy 1"
Cost  4: Trauma Team [DAN]  P=0, H=4 (mean P+H=6.5)
         "Tap -> Remove 1 damage counter from one of your Characters. If that Character is..."
Cost  4: Bendu (A) [FOR]  P=0, H=4 (mean P+H=6.5)
         "Bendu doesn't count toward controlling any arena. | Prevent all damage to and fr..."
Cost  4: Bail's Speeder (A) [FOTR]  P=1, H=3 (mean P+H=6.5)
         "Pay 1 Force -> Prevent 1 damage to one of your Jedi in the Ground arena. You may..."
Cost  4: Executioner Cart [JG]  P=2, H=2 (mean P+H=6.5)
         "Tap -> Choose one of your opponent's units in the Character arena. That unit can..."
Cost  4: Jedi Airhooks [RO2]  P=2, H=2 (mean P+H=6.5)
         "Accuracy 2 | Pay 1 Force -> Evade 2"
Cost  4: Rogue Seven (A) [RS]  P=2, H=2 (mean P+H=6.5)
         "Switch: +1 health/+1 power | Each of your other Rogue Starfighters gets "Pay 0 F..."
Cost  4: Imperial Mobile Surgical Unit [SOLO]  P=2, H=2 (mean P+H=6.5)
         "Reserves: Tap -> Prevent 1 damage to one of your Imperials in the Ground or Char..."
Cost  4: Dai Bendu Monks [TAL]  P=0, H=4 (mean P+H=6.5)
         "When you deploy this unit, if you have a Tho Yor in any arena, put 1 mastery cou..."
Cost  4: Keshiri Citizens [TAL]  P=2, H=2 (mean P+H=6.5)
         "Reserves: Tap -> Choose one: Gain 1 Force. Or: Gain 1 build point. Play only dur..."
Cost  4: Kashyyyk Skyhook [TDT]  P=0, H=4 (mean P+H=6.5)
         "Shields 1 | When the Ground battle step starts, choose up to X of your opponent'..."
Cost  4: Throne Room Attendants [TLJ]  P=0, H=4 (mean P+H=6.5)
         "Alternative Cost: Pay 2 build points, tap one of your Supreme Leaders. | Tap -> ..."
Cost  4: Porg Family [TLJ]  P=0, H=4 (mean P+H=6.5)
         "Tap -> Take 1 10/0/1 Porglets Subordinate with "As long as you have a non-Subord..."
Cost  4: Farmer Repulsorlift  [TM]  P=0, H=4 (mean P+H=6.5)
         "Tap -> Search your deck for a Character unit card, show it to your opponent, and..."
Cost  4: Arvala Jawa Traders [TM]  P=1, H=3 (mean P+H=6.5)
         "Tap, Remove an Equipment card with printed build cost X from your hand from the ..."
Cost  4: Nevarro Repulsorlift [TM]  P=0, H=4 (mean P+H=6.5)
         "When you deploy this unit, take 1 20/0/2 R6 Droid Pilot Subordinate with "[Pilot..."
Cost  4: Ahch-To Porgs [TROS]  P=0, H=4 (mean P+H=6.5)
         "When you deploy this unit to any arena, choose one: Remove 1 damage counter from..."
Cost  4: Sh'rip Sh'pa [TUF]  P=0, H=4 (mean P+H=6.5)
         "Tap -> Add X+1 counters to your Resource, where X is the number of Locations you..."
Cost  4: ExGal Listening Post [VP]  P=0, H=4 (mean P+H=6.5)
         "Shields 1 | When the battle phase starts, you may choose a unit with Stealth in ..."
Cost  5: Snowtrooper Platoon [TFA]  P=1, H=1 (mean P+H=7.9)
         "Critical Hit 1 | This unit gets +1 power and +1 health for each Arctic unit you ..."
Cost  5: Jedi Spirits (C) [ALTA]  P=0, H=3 (mean P+H=7.9)
         "Stack: Any Jedi Spirit. | Jedi Spirits doesn't count toward controlling any aren..."
Cost  5: Grievous's Starfighter (C) [CAD]  P=0, H=3 (mean P+H=7.9)
         "Switch: +3 power, Accuracy 1/Stealth | Discard a card from your hand -> Search y..."
Cost  5: Jedi Spirits (B) [BAE]  P=0, H=4 (mean P+H=7.9)
         "Stack: Any Jedi Spirit. | Jedi Spirits doesn't count toward controlling any aren..."
Cost  5: Rey's Speeder (A) [TFA]  P=0, H=4 (mean P+H=7.9)
         "Whenever one of your non-unit cards would be discarded, you may put it beneath R..."
Cost  5: Jedi Spirits (A) [TROS]  P=0, H=4 (mean P+H=7.9)
         "Upkeep: Gain 2 Force. | Jedi Spirits doesn't count toward controlling any arena...."
Cost  5: Imperial Detention Block [ANH]  P=1, H=4 (mean P+H=7.9)
         "[tap] -> Choose an untapped non-Jedi Character. Tap that Character. Play only du..."
Cost  5: Exegol Navigation Tower (A) [BAE]  P=0, H=5 (mean P+H=7.9)
         "Armor | When the Space battle step starts, put 1 mastery counter on each of your..."
Cost  5: Force Priestesses (A) [BL]  P=0, H=5 (mean P+H=7.9)
         "Force Priestesses doesn't count toward controlling the Ground or Character arena..."
Cost  5: Elite Nightsister Squad [BL]  P=1, H=4 (mean P+H=7.9)
         "Treat this unit as a Force Sensitive. | This unit gets +1 power for each other N..."
Cost  5: Separatist Mutant Horde [CWSO]  P=3, H=2 (mean P+H=7.9)
         "Fury 3 | Discard this unit from this arena -> Put 2 damage counters on one of yo..."
Cost  5: Gungan Artillery [ION]  P=0, H=5 (mean P+H=7.9)
         "Whenever this unit attacks, you may reveal a Gungan unit card in your hand and r..."
Cost  5: Munitions Wagon [ION]  P=1, H=4 (mean P+H=7.9)
         "[tap], Pay 2 Force -> Choose an arena. Each of your Gungans in that arena gets +..."
Cost  5: Republic Drop Ship [SR]  P=2, H=3 (mean P+H=7.9)
         "When you deploy this unit, you get +2 build points this turn. | Shields 1"
Cost  5: The Erased [TDT]  P=0, H=5 (mean P+H=7.9)
         "Tap -> Choose one of your unique Characters. The chosen Character loses its name..."
Cost  5: Undisputed Victor (A) [TLJ]  P=0, H=5 (mean P+H=7.9)
         "As long as Baron Yasto Attsmun is in any arena or your build zone, Undisputed Vi..."
Cost  5: Fulminatrix Cannon Tower [TLJ]  P=0, H=5 (mean P+H=7.9)
         "Each Starfighter gets Accuracy 2 when attacking this unit. | This unit gets Crit..."
Cost  5: Thrall Herder [VP]  P=1, H=4 (mean P+H=7.9)
         "Armor | When you deploy this unit, take 2 60/2/1 Thrall Swarm Subordinates and p..."
Cost  5: Abersyn Symbiote [WAE]  P=2, H=3 (mean P+H=7.9)
         "Upkeep: Put 1 captivity counter on a unit. | [tap] -> One of your opponent's Gro..."
Cost  6: Tyranus's Geonosian Speeder (A) [AOTC]  P=2, H=1 (mean P+H=9.4)
         "[tap] -> Search your deck. You may take a Battle card from your deck. Show it to..."
Cost  6: Slave Divers [DAN]  P=0, H=4 (mean P+H=9.4)
         "This unit costs 1 less build counter to deploy for each Slave you have in any ar..."
Cost  6: Luke's Illusion (B) [ALTA]  P=0, H=5 (mean P+H=9.4)
         "Treat Luke's Illusion as Luke Skywalker. | Luke's Illusion can't attack. | Each ..."
Cost  6: Luke's Illusion (B) (Promo) [ALTA]  P=0, H=5 (mean P+H=9.4)
         "Treat Luke's Illusion as Luke Skywalker. | Luke's Illusion can't attack. | Each ..."
Cost  6: Atmospheric Assault Lander [TFA]  P=1, H=4 (mean P+H=9.4)
         "When you deploy this unit, you may pay 3 build points. If you do, take 1 50/4/2 ..."
Cost  6: Poe's Starfighter (F) [BAE]  P=3, H=3 (mean P+H=9.4)
         "Switch: Shields 1/Velocity 10 | Accuracy 1 | Each of your opponent's units in th..."
Cost  6: Poe's Ski Speeder (A) [BOC]  P=3, H=3 (mean P+H=9.4)
         "Inspiration | Resilience 2 | When you deploy Poe's Ski Speeder, you may search y..."
Cost  6: Blue Three (B) [BOSB]  P=3, H=3 (mean P+H=9.4)
         "Switch: Accuracy 1/Double Damage | When you deploy Blue Three, you may search yo..."
Cost  6: Poe's Starfighter (C) [BOSB]  P=3, H=3 (mean P+H=9.4)
         "Switch:  Accuracy 1/Inspiration | As long as Poe's Starfighter has a Pilot, each..."
Cost  6: Red Four (B) [BOSB]  P=3, H=3 (mean P+H=9.4)
         "Switch: Focus 1/Double Strike | When you deploy Red Four, you may remove 1 damag..."
Cost  6: Wedge's Snowspeeder (A) [ESB]  P=3, H=3 (mean P+H=9.4)
         "When Wedge's Snowspeeder damages another unit, until end of turn, each of your o..."
Cost  6: Mon Mothma (F) [FOR]  P=3, H=3 (mean P+H=9.4)
         "Inspiration | As long as you have another Rebel in this arena, Mon Mothma gets S..."
Cost  6: Corellian Maglev Train [JK]  P=0, H=6 (mean P+H=9.4)
         "Armor | Each of your other Ground units gets +10 speed. | Tap -> Add 2 counters ..."
Cost  6: Sebulba's Podracer (A) [PM]  P=2, H=4 (mean P+H=9.4)
         "[tap] -> Put 3 damage counters on a unit in the Ground arena and 1 damage counte..."
Cost  6: GR-75 Medium Transport [RS]  P=1, H=5 (mean P+H=9.4)
         "Switch: Lucky 1/Shields 1 | Tap -> Gain 2 build points. Play only during your bu..."
Cost  6: TIE Bomber Squadron  [RS]  P=3, H=3 (mean P+H=9.4)
         "Switch:  Bombard 3/+2 power | Hidden Cost 4 | As long as you have an Imperial Of..."
Cost  6: Clone Bomb Squad [AGD]  P=3, H=4 (mean P+H=9.4)
         "Your opponent can't do damage to your units in the Ground or Character arena usi..."
Cost  6: Fortitude (A) [BAE]  P=2, H=5 (mean P+H=9.4)
         "[Tap], Move Fortitude from the Space arena to the Ground arena -> Each of your R..."
Cost  6: Fortitude (B) [BAE]  P=2, H=5 (mean P+H=9.4)
         "Switch: Shields 1/Armor | Each of your Pilots gets Fortitude. | [Tap] -> Search ..."
Cost  6: Sarlacc (E) [BOBF]  P=1, H=6 (mean P+H=9.4)
         "Armor | Any unit that Sarlacc attacks must attack Sarlacc with -3 power for its ..."
Cost  6: Separatist Council (B) [CAD]  P=3, H=4 (mean P+H=9.4)
         "INSERT: Each of your Commerce Guild, Trade Federation, Corporate Alliance, IG Ba..."
Cost  6: Lady Luck (B) [ER]  P=3, H=4 (mean P+H=9.4)
         "Switch: +40 speed/Stealth | Whenever Lady Luck is attacked, roll a die. If you r..."
Cost  6: Jedi Shadow [JEDI]  P=3, H=4 (mean P+H=9.4)
         "Switch: Precision/+1 power | Stealth | This unit gets Critical Hit 3 when attack..."
Cost  6: Objurium (A) [RS]  P=2, H=5 (mean P+H=9.4)
         "Switch: Lucky 1/+1 health | When you deploy Objurium, you may pay 1 build point...."
Cost  6: Augie's Great Municipal Band (A) [TEN]  P=1, H=6 (mean P+H=9.4)
         "When the Ground battle step ends, gain X Force, where X is the number of Gingans..."
Cost  6: Vigil (A) [TLJ]  P=2, H=5 (mean P+H=9.4)
         "Switch: +10 speed/+1 health | Remove 2 counters from your Resource -> Prevent al..."
Cost  6: Gideon's Outland TIE Fighter (C) [TM]  P=3, H=4 (mean P+H=9.4)
         "Switch: Stealth/Armor | Whenever you deploy a Remnant Stormtrooper to the Ground..."
Cost  6: Sith Master and Apprentice (O) [VV1]  P=1, H=6 (mean P+H=9.4)
         "Deploy: Put 2 corruption counters on one of your opponent's Jedi. | Foresight: D..."
Cost  7: Bor Gullet [RO]  P=0, H=6 (mean P+H=10.6)
         "Upkeep: Look at your opponent's hand, and you may discard a card from his or her..."
Cost  7: Sw-0608 (B) [RO]  P=2, H=4 (mean P+H=10.6)
         "Switch: Stealth/Damage Control 1 | SW-0608 can have up to 2 Pilots. | When you d..."
Cost  7: Vader's Interceptor (B) [TDT]  P=3, H=3 (mean P+H=10.6)
         "Hidden Cost 4 | Double Strike | Pay 1 Force -> Evade 2 | INSERT: Pay 1 Force -> ..."
Cost  7: Poe's Starfighter (B) [TFA]  P=3, H=3 (mean P+H=10.6)
         "Switch:+10 speed/+1 power | Accuracy 2 | Double Strike"
Cost  7: Kindalo [BL]  P=2, H=5 (mean P+H=10.6)
         "Switch: Shields 2/Damage Control 1 | When your build step starts, roll a die. If..."
Cost  7: Last Resort (A) [DAN]  P=2, H=5 (mean P+H=10.6)
         "Lucky 2 | When the Space battle step starts, you may choose one of your Transpor..."
Cost  7: SW-0608 (A) [RO]  P=3, H=4 (mean P+H=10.6)
         "Sw-0608 can have up to 2 Pilots. | Stealth | When you deploy SW-0608, you may se..."
Cost  7: TIE Striker Squadron [RO]  P=3, H=4 (mean P+H=10.6)
         "Switch: +1 health/+10 speed, Fury 1 | Precision | Double Strike | Pay 2 Force ->..."
Cost  7: Clone Facility [SR]  P=2, H=5 (mean P+H=10.6)
         "[tap] -> Search your deck. You may take a clone card from your deck. Show it to ..."
Cost  7: KT-400 Military Droid Carrier [TOR]  P=3, H=4 (mean P+H=10.6)
         "When you deploy this unit, take 3 40/2/1 Military Droid Subordinates with "Accur..."
Cost  8: Yorik-trema-Class Carrier [VP]  P=1, H=4 (mean P+H=11.6)
         "Damage Control 1 | When you deploy this unit, take 2 40/3/3 Yuuzhan Vong Warrior..."
Cost  8: Sarlacc (A) [ROTJ]  P=1, H=6 (mean P+H=11.6)
         "You may choose not to untap Sarlacc during your untap step. | [tap] -> Choose on..."
Cost  8: Loyalist Committee (A) [AGD]  P=4, H=4 (mean P+H=11.6)
         "Stack: Any unique Diplomat Character. | Hidden Cost 6 | As long as you have at l..."
Cost  8: Alliance High Command (C) [ALTA]  P=4, H=4 (mean P+H=11.6)
         "Stack: Any unique Rebel Officer. | Alliance High Command can have up to 6 cards ..."
Cost  8: Nite Owls (A) [BL]  P=4, H=4 (mean P+H=11.6)
         "Switch: Double Strike/Accuracy 1 | Whenever Nite Owls is attacked, you may pay 3..."
Cost  8: Millennium Falcon (B2) [BOC]  P=3, H=5 (mean P+H=11.6)
         "Switch: +2 power/Double Strike | The Millennium Falcon gets Critical Hit 2 when ..."
Cost  8: Resistance High Command (A) [BOC]  P=4, H=4 (mean P+H=11.6)
         "Stack: Any unique Resistance Officer. | Damage Control 2 | Inspiration | Each of..."
Cost  8: Elite Galactic Marines (A) [CAD]  P=4, H=4 (mean P+H=11.6)
         "Switch: Double Strike / Elude | Accuracy 2"
Cost  8: Mutant Horde [CWSO]  P=4, H=4 (mean P+H=11.6)
         "Fury 2 | When this unit is discarded from any arena, you may pay 3 Force. If you..."
Cost  8: Alliance High Command (B) [RO]  P=4, H=4 (mean P+H=11.6)
         "Stack: Any unique Rebel Officer. | Stealth | As long as you have at least 3 Rebe..."
Cost  8: Alliance High Command (A) [TEN]  P=4, H=4 (mean P+H=11.6)
         "Stack: Any unique Rebel Officer. | Inspiration | Each of your Rebels costs 1 les..."
Cost  9: Droideka Squad [CAD]  P=4, H=4 (mean P+H=12.9)
         "Switch: +20 speed / Accuracy 1 | Treat this unit as a Separatist. | Shields 2 | ..."
Cost 11: Bastila Shan (C) [KAE]  P=4, H=6 (mean P+H=16.3)
         "Each of your other Old Republic units gets Accuracy 1 and Lucky 1. | Double Stri..."
Cost 11: Bastila Shan (C) (Promo) [KAE]  P=4, H=6 (mean P+H=16.3)
         "Each of your other Old Republic units gets Accuracy 1 and Lucky 1. | Double Stri..."
Cost 12: Seismic Tank [RAW]  P=0, H=8 (mean P+H=17.0)
         "Armor | Stun 4 | This unit loses Armor as long as it is being attacked by a Jedi..."
Cost 14: Abeloth (A) [15TH]  P=9, H=9 (mean P+H=20.6)
         "Stack: Any unique unit with "Force in its game text or subtype. | Upkeep: Gain 1..."
Cost 15: Separatist Droid Legion [BL]  P=8, H=10 (mean P+H=22.1)
         "Switch: This unit can attack units in the Character arena./This unit can attack ..."
```


## Character (3682 cards)

**Regression model** (Ridge) — n=3654, R^2=0.818, RMSE=0.91, alpha=6.615

```
Predictor                      Coeff
-------------------------------------
Constant                       0.215
power                          0.437
health                         0.628
Evade                          0.015
Accuracy                       0.403
Critical Hit                  -0.023
Armor                          0.385
Deploy                         0.460
Stealth                        0.317
Fury                          -0.038
Lucky                          0.018
Deflect                        0.285
Bounty                        -0.063
Upkeep                        -0.138
Retaliate                      0.008
Parry                          0.315
Hidden Cost                    0.218
Reserves                       0.248
Intercept                     -0.142
Protect                        0.008
Stack                          0.394
Absorb                         0.068
Damage Control                 0.189
Pilot                          0.203
Focus                          0.155
Alternative Cost               0.033
Foresight                      0.028
Inspiration                    1.125
Double Strike                  0.604
Resilience                     0.019
Precision                     -0.056
Ferocity                       0.477
Stun                           0.125
Persuade                      -0.221
Riposte                        0.174
Forewarning                    0.313
Ambush                         0.043
Overkill                       0.464
Avenge                         0.062
Reduced Cost                  -0.179
Redirect                       0.080
Meditate                      -0.054
Backfire                      -0.039
Accuracy (x power)            -0.037
Critical Hit (x power)         0.044
Fury (x power)                 0.037
freeform_count                 0.240
army_count                     0.254
prevention_ceiling             0.147
prevention_force_cost         -0.001
protect_ceiling                0.008
protect_force_cost            -0.107
retaliate_ceiling              0.008
retaliate_force_cost           0.022
ambush_ceiling                 0.043
ambush_force_cost             -0.015
is_unique                      0.260
multi_arena                    0.526
```

_Note: Ridge coefficients are regularized toward zero. Interaction terms (power x keyword) capture scaling effects._

**Cost curve:**

```
Cost |    N | Avg P | Avg H | Avg P+H | P range | H range
----------------------------------------------------------
   1 |    5 |   0.4 |   1.0 |     1.4 | 0-1    | 1-1
   2 |  131 |   1.5 |   2.1 |     3.6 | 0-4    | 1-5
   3 |  395 |   2.0 |   2.7 |     4.8 | 0-5    | 1-6
   4 |  614 |   2.8 |   3.4 |     6.2 | 0-6    | 1-6
   5 |  672 |   3.6 |   4.2 |     7.8 | 0-6    | 2-8
   6 |  684 |   4.4 |   4.9 |     9.3 | 0-7    | 2-8
   7 |  473 |   5.0 |   5.4 |    10.3 | 0-8    | 1-9
   8 |  309 |   5.6 |   5.7 |    11.3 | 1-8    | 3-9
   9 |  191 |   6.2 |   6.2 |    12.4 | 3-9    | 4-9
  10 |   85 |   6.6 |   6.8 |    13.4 | 4-9    | 5-12
  11 |   48 |   7.0 |   7.0 |    14.1 | 4-9    | 6-9
  12 |   25 |   8.0 |   8.1 |    16.1 | 4-12   | 6-12
  13 |   15 |   8.1 |   8.1 |    16.2 | 4-10   | 7-9
  14 |    4 |   9.8 |   9.8 |    19.5 | 9-10   | 9-10
  15 |    3 |   9.0 |  10.7 |    19.7 | 8-10   | 10-12
```

**Keyword frequency by cost tier:**

```
Cost  1: Reserves (40%), Upkeep (20%), Stack (20%), Accuracy (20%), Backfire (20%)
Cost  2: Pilot (10%), Deploy (8%), Reserves (8%), Lucky (8%), Upkeep (5%)
Cost  3: Reserves (8%), Deploy (8%), Evade (7%), Lucky (6%), Accuracy (6%)
Cost  4: Reserves (9%), Evade (9%), Critical Hit (8%), Deploy (7%), Lucky (7%)
Cost  5: Evade (19%), Accuracy (12%), Critical Hit (11%), Stealth (8%), Lucky (7%)
Cost  6: Evade (23%), Accuracy (12%), Armor (11%), Critical Hit (10%), Stealth (10%)
Cost  7: Evade (32%), Armor (15%), Accuracy (15%), Critical Hit (12%), Deploy (12%)
Cost  8: Evade (31%), Armor (20%), Critical Hit (16%), Fury (13%), Retaliate (12%)
Cost  9: Evade (41%), Armor (24%), Accuracy (15%), Critical Hit (15%), Bounty (10%)
Cost 10: Evade (43%), Deflect (21%), Armor (20%), Stack (19%), Critical Hit (17%)
Cost 11: Evade (48%), Deflect (33%), Accuracy (21%), Fury (19%), Inspiration (19%)
Cost 12: Deploy (52%), Armor (32%), Inspiration (28%), Evade (20%), Critical Hit (20%)
Cost 13: Velocity (24%), Evade (24%), Inspiration (18%), Alternative Cost (18%), Armor (18%)
```

**Stat-weak cards** (P+H > 1.5 SD below cost-tier mean -- likely have significant abilities):

```
Cost  2: Binding Energy [ALTA]  P=0, H=2 (mean P+H=3.6)
         "You may stack this card beneath any unit, and there can only be one copy of this..."
Cost  2: Morley (A) [BL]  P=1, H=1 (mean P+H=3.6)
         "When you deploy Morley, you may search your deck for up to 2 Nightbrother unit c..."
Cost  2: Silman (A) [BL]  P=1, H=1 (mean P+H=3.6)
         "Upkeep: Each player pays 1 Force. | When Silman is discarded from the Character ..."
Cost  2: LEP-Series Service Droid [BOBF]  P=1, H=1 (mean P+H=3.6)
         "When you deploy this unit and when it is discarded, you may put or remove 1 cred..."
Cost  2: Boba Fett (P) [CAD]  P=1, H=1 (mean P+H=3.6)
         "INSERT: Treat Boba as a Clone. | INSERT: Each Clone gets -2 power when attacking..."
Cost  2: Meal Droid [ER]  P=0, H=2 (mean P+H=3.6)
         "Tap, Discard a unique unit card from your hand -> Remove up to 2 damage counters..."
Cost  2: Naboo Soldier [ION]  P=1, H=1 (mean P+H=3.6)
         "Fury 1 | This unit gets +1 power and +1 health for each Naboo unit in the Charac..."
Cost  2: Kouhun [JG]  P=1, H=1 (mean P+H=3.6)
         "Tap, Discard this unit from the Character arena -> Choose one of your opponent's..."
Cost  2: Scurrier [JG]  P=1, H=1 (mean P+H=3.6)
         "As long as this unit is in the Character arena, it gets +2 power for each other ..."
Cost  2: Gizka [KAE]  P=1, H=1 (mean P+H=3.6)
         "Reduced Cost 1: If a Gizka is in any arena. | Tap -> One of your opponent's Grou..."
Cost  2: Naboo Pilot [PM]  P=1, H=1 (mean P+H=3.6)
         "[Pilot] Starfighter Pilot. The Starfighter gets Lucky 1."
Cost  2: Grogu (D) [TM]  P=0, H=2 (mean P+H=3.6)
         "Pay 0 Force -> Evade 2 | INSERT: When Grogu is discarded, you may pay 1 Force. I..."
Cost  2: Nevarro RA-7 [TM]  P=0, H=2 (mean P+H=3.6)
         "When your opponent's retreat step ends, each player may add 1 counter to his or ..."
Cost  2: Moff Gideon's Hologram [TMW]  P=0, H=2 (mean P+H=3.6)
         "Moff Gideon's Hologram doesn't count toward controlling any arena. | Moff Gideon..."
Cost  2: Lava Meerkat [TMW]  P=1, H=1 (mean P+H=3.6)
         "When this unit is discarded, add 1 counter to your Resource. | Each of your unit..."
Cost  3: Mouse Droid [ANH]  P=0, H=1 (mean P+H=4.8)
         "[tap], Pay 1 build point -> Draw a card. Play only during your build step."
Cost  3: Qui-Gon's Spirit [AGD]  P=0, H=2 (mean P+H=4.8)
         "Qui-Gon's Spirit doesn't count toward controlling the Character arena. | Prevent..."
Cost  3: R3-S6 (A) [AGD]  P=0, H=2 (mean P+H=4.8)
         "When the Character battle step starts, treat R3-S6 as a Light Side unit. | R3-S6..."
Cost  3: Rotta the Hutt [AGD]  P=1, H=1 (mean P+H=4.8)
         "You may stack Rotta under Jabba the Hutt. | Rotta can't be on top of Jabba's sta..."
Cost  3: Todo 360 (A) [AGD]  P=0, H=2 (mean P+H=4.8)
         "Alternative Cost: Tap Cad Bane. | Tap -> Your opponent discards card at random f..."
Cost  3: Yoda's Spirit (C) [ALTA]  P=0, H=2 (mean P+H=4.8)
         "Yoda's Spirit doesn't count toward controlling any arena. | Prevent all damage t..."
Cost  3: Hologram [ALTA]  P=0, H=2 (mean P+H=4.8)
         "This unit doesn't count toward controlling any arena. | Prevent all damage to an..."
Cost  3: Hologram (Promo 1) [ALTA]  P=0, H=2 (mean P+H=4.8)
         "This unit doesn't count toward controlling any arena. | Prevent all damage to an..."
Cost  3: Hologram (Promo 2) [ALTA]  P=0, H=2 (mean P+H=4.8)
         "This unit doesn't count toward controlling any arena. | Prevent all damage to an..."
Cost  3: Imperial Sentry Droid [ANH]  P=1, H=1 (mean P+H=4.8)
         "When the battle phase ends, if this unit is the Character arena, look at your op..."
Cost  3: C-3PO (Q) [BOC]  P=0, H=2 (mean P+H=4.8)
         "Reserves: Tap -> Draw a card. Play only during your build step."
Cost  3: Salacious B. Crumb (C) [BOTS]  P=1, H=1 (mean P+H=4.8)
         "Treat Salacious as a Crime Gang Entertainer. | Alternative Cost: Remove 3 counte..."
Cost  3: Battle Droid Marine [CWSO]  P=1, H=1 (mean P+H=4.8)
         "Switch: +1 power / +1 health | Whenever this unit would take 2 or less damage, i..."
Cost  3: Yoda (G) [ESB]  P=1, H=1 (mean P+H=4.8)
         "When Yoda you deploy, under any Jedi Padawan, one copy of Yoda stack you can. On..."
Cost  3: Exar Kun's Spirit (A) [JK]  P=0, H=2 (mean P+H=4.8)
         "Exar Kun's Spirit doesn't count toward controlling the Character arena. | Preven..."
Cost  3: Darth Andeddu's Spirit (A) [LEG]  P=0, H=2 (mean P+H=4.8)
         "This unit doesn't count for arena control. | Prevent all damage to and from this..."
Cost  3: Anakin Skywalker (J) [PM]  P=1, H=1 (mean P+H=4.8)
         "Pay 1 Force -> Evade 1 | [Pilot] Speeder and Starfighter Pilot. The Speeder or S..."
Cost  3: R2-D2 (H) [RAS]  P=1, H=1 (mean P+H=4.8)
         "Any Starfighter with R2-D2 on it can have an extra Pilot if that Pilot isn't an ..."
Cost  3: Laa (A) [RO2]  P=0, H=2 (mean P+H=4.8)
         "When Laa is attacked, the attack ends unless your opponent pays 4 Force. | Preve..."
Cost  3: Salacious B. Crumb (A) [ROTJ]  P=1, H=1 (mean P+H=4.8)
         "[tap] -> Choose one of your opponent's units and one of your units in the same a..."
Cost  3: Yoda's Spirit (A) [ROTJ]  P=0, H=2 (mean P+H=4.8)
         "Yoda's Spirit does not count toward controlling the Character arena. | Prevent a..."
Cost  3: Salacious B. Crumb (B) [TEN]  P=1, H=1 (mean P+H=4.8)
         "When your build step starts, you may choose one: Put 1 counter of any type on an..."
Cost  3: Din Djarin's Hologram (A) [TMW]  P=0, H=2 (mean P+H=4.8)
         "Din Djarins Hologram doesnt count toward controlling any arena. | Din Djarins..."
Cost  3: Grogu (H) [TMW]  P=1, H=1 (mean P+H=4.8)
         "Treat Grogu as a Jedi Padawan. | You may stack Grogu beneath one of your unique ..."
Cost  4: EV-A4-D (A) [AGD]  P=0, H=2 (mean P+H=6.2)
         "X, Discard X cards from your hand -> Remove X damage counters from one of your C..."
Cost  4: Anakin's Spirit (B) [ALTA]  P=0, H=2 (mean P+H=6.2)
         "Anakin's Spirit doesn't count toward controlling any arena. | Prevent all damage..."
Cost  4: Darth Bane's Spirit (A) [BL]  P=0, H=2 (mean P+H=6.2)
         "Darth Bane's Spirit doesn't count toward controlling the Character arena. | Prev..."
Cost  4: Chewbacca's Porg (B) [BOC]  P=0, H=2 (mean P+H=6.2)
         "Transport Pilot. The Transport gets:  -This unit can have an extra Pilot.  - Whe..."
Cost  4: Vulptex [BOC]  P=1, H=1 (mean P+H=6.2)
         "When you deploy this unit, you may look at your opponent's hand and partially bu..."
Cost  4: Vulptex (Promo) [BOC]  P=1, H=1 (mean P+H=6.2)
         "When you deploy this unit, you may look at your opponent's hand and partially bu..."
Cost  4: Spacetrooper [ER]  P=0, H=2 (mean P+H=6.2)
         "Switch: +1 health/+2 power, Ion Cannon 2 | Armor | As long as this unit is in th..."
Cost  4: Qui-Gon's Spirit (C) [OBWN]  P=0, H=2 (mean P+H=6.2)
         "Qui-Gon's Spirit doesn't count toward arena control. | Prevent all damage to and..."
Cost  4: Commander Nemet (A) [RAS]  P=1, H=1 (mean P+H=6.2)
         "When your build step starts, look at the top card of your opponent's deck. You m..."
Cost  4: Anakin's Spirit (A) [ROTJ]  P=0, H=2 (mean P+H=6.2)
         "Anakin's Spirit doesn't count toward controlling the Character arena. | Prevent ..."
Cost  4: Ben's Spirit (A) [UNION]  P=0, H=2 (mean P+H=6.2)
         "Ben's Spirit doesn't count toward arena control. | Prevent all damage to and fro..."
Cost  4: General Leia Organa Solo (K2) [15TH]  P=0, H=3 (mean P+H=6.2)
         "Switch: Damage Control 2/+2 power, Lucky 2 | Leia doesn't count toward controlli..."
Cost  4: R2-D2 (O) [AGD]  P=1, H=2 (mean P+H=6.2)
         "Alternative Cost: Tap Anakin Skywalker, Anakin's Starfighter or Azure Angel. | A..."
Cost  4: 99 (A) [AGD]  P=1, H=2 (mean P+H=6.2)
         "Lucky 1 | When 99 is discarded from the Character arena, you gain X Force, where..."
Cost  4: Karness's Spirit (B) [LEG]  P=0, H=3 (mean P+H=6.2)
         "Karness's Spirit doesn't count for arena control. | Prevent all damage to and fr..."
Cost  4: Luke's Spirit (C) [LEG]  P=0, H=3 (mean P+H=6.2)
         "Luke's Spirit doesn't count for arena control. | Prevent all damage to and from ..."
Cost  4: Mara's Spirit (A) [LEG]  P=0, H=3 (mean P+H=6.2)
         "Mara's Spirit doesn't count for arena control. | Prevent all damage to and from ..."
Cost  4: Duchess Satine Kryze (A) [MAND]  P=0, H=3 (mean P+H=6.2)
         "Reserves: [tap], Put 1 card from the top of your opponent's deck into the discar..."
Cost  4: Finis Valorum (B) [PM]  P=1, H=2 (mean P+H=6.2)
         "[tap] -> You gain 1 Force, gain 1 build point, and draw a card. Play only during..."
Cost  4: BB-8 (A) [TFA]  P=0, H=3 (mean P+H=6.2)
         "Alternative Cost: Tap Poe Dameron or Rey. | As long as you have Poe Dameron or R..."
Cost  4: BB-8 (B) [TFA]  P=0, H=3 (mean P+H=6.2)
         "As long as you have Poe Dameron in any arena, you may attach Starchart Memory Dr..."
Cost  4: BB-8 (A) (LEGO) [TFA]  P=0, H=3 (mean P+H=6.2)
         "Alternative Cost: Tap Poe Dameron or Rey. | As long as you have Poe Dameron or R..."
Cost  4: IT-SOO.2 Medical Droid [TLJ]  P=0, H=3 (mean P+H=6.2)
         "Reserves: Tap, Remove X counters from your Resource -> Remove X damage counters ..."
Cost  4: Jango Fett (M) [AAA]  P=2, H=2 (mean P+H=6.2)
         "Each of your Mandalorians gets Focus 2 | During your build step, you may remove ..."
Cost  4: Daughter (A) [AGD]  P=0, H=4 (mean P+H=6.2)
         "Daughter doesn't count toward controlling the Character arena. | Prevent all dam..."
Cost  4: Tee Wat Kaa (A) [AGD]  P=0, H=4 (mean P+H=6.2)
         "Each of your other Lurmen in the Ground and Character arena  gets -3 power, +1 h..."
Cost  4: Boba Fett (N) [AGD]  P=2, H=2 (mean P+H=6.2)
         "Each of your opponent's Clones gets -1 power. | Tap -> Tap one of your opponent'..."
Cost  4: IT-0 Interrogator Droid [ANH]  P=1, H=3 (mean P+H=6.2)
         "[tap] -> Look at your opponent's hand. If there are any Battle or Mission cards ..."
Cost  4: URoRRuR'R'R (A) [ANH]  P=2, H=2 (mean P+H=6.2)
         "As long as you have more units in the Character arena than your opponent, URoRRu..."
Cost  4: R2-D2 (C) [ANH]  P=1, H=3 (mean P+H=6.2)
         "[tap] -> Look at the top 3 cards of your opponent's deck. Put them back in any o..."
Cost  4: Fodesinbeed Annodue (A) [BEP]  P=2, H=2 (mean P+H=6.2)
         "Reduced Cost 3: If a Podracer is in any arena. | Whenever you move a Pilot to a ..."
Cost  4: Watto (C) [BEP]  P=2, H=2 (mean P+H=6.2)
         "Intimidation | Roll a die -> Persuade 2 if you roll a 3 or more. | Reserves: [Ta..."
Cost  4: Tracking Droid [BH]  P=0, H=4 (mean P+H=6.2)
         "Pay 2 Force -> Move a Character from your opponent's build zone to its arena tap..."
Cost  4: AZI-3 (A) [BL]  P=1, H=3 (mean P+H=6.2)
         "As long as Fives is in any arena, AZI-3 gets "Whenever AZI-3 would be damaged, y..."
Cost  4: Byph (A) [BL]  P=1, H=3 (mean P+H=6.2)
         "Each Force Sensitive costs 1 less build counter to deploy. | Pay 3 Force -> Defl..."
Cost  4: Duchess Satine Kryze (C) [BL]  P=0, H=4 (mean P+H=6.2)
         "Upkeep: Put 1 captivity counter on Satine or tap her. | When Satine has 4 or mor..."
Cost  4: WAC-47 (A) [BL]  P=2, H=2 (mean P+H=6.2)
         "Lucky 2 | Transport Pilot. The Transport gets: -Whenever this unit is damaged by..."
Cost  4: Grogu (J) [BOBF]  P=0, H=4 (mean P+H=6.2)
         "Foresight: Put 1 mastery counter on Grogu. | Forewarning: Gain 2 Force. | Pay 1 ..."
Cost  4: BB-8 (E) [BOC]  P=2, H=2 (mean P+H=6.2)
         "When you deploy BB-8, you may roll a die. If you do, and roll a 5 or 6, gain con..."
Cost  4: BB-9E (B) [BOC]  P=1, H=3 (mean P+H=6.2)
         "Lucky 1 | When your build step starts, look at your opponent's hand. If there ar..."
Cost  4: Captain Geno Namit (A) [BOC]  P=1, H=3 (mean P+H=6.2)
         "Reserves: Tap, Remove 1 counter from your Resource -> Search your deck for a Bat..."
Cost  4: Imperial Walker Gunner [BOH]  P=2, H=2 (mean P+H=6.2)
         "[Pilot] Walker Pilot. The Walker gets: * +2 power. * Accuracy 1. * This unit can..."
Cost  4: Rogue Pilot [BOH]  P=2, H=2 (mean P+H=6.2)
         "[Pilot] Speeder and Starfighter Pilot. The Speeder or Starfighter gets: * +1 pow..."
Cost  4: BB-8 (C) [BOSB]  P=2, H=2 (mean P+H=6.2)
         "Lucky 2 | Starfighter Pilot. The Starfighter gets:  -This unit can have up to 2 ..."
Cost  4: Commander Willard (A) [BOY]  P=2, H=2 (mean P+H=6.2)
         "As long as Willard is in the Character arena, each of your Starfighters gets Shi..."
Cost  4: Skakoan Engineer [CWSO]  P=2, H=2 (mean P+H=6.2)
         "Tap -> Each of your Mutants cost 1 less built counter to deploy until end of tur..."
Cost  4: GG-Series Hospitality Droid [DAN]  P=1, H=3 (mean P+H=6.2)
         "Tap, Pay 1 build point -> Draw 2 cards and discard a card from your hand. If the..."
Cost  4: R2-D2 (N) [EE]  P=1, H=3 (mean P+H=6.2)
         "Alternative Cost: Tap Luke Skywalker. | As long as you have Luke Skywalker in th..."
Cost  4: Tem Merkon (A) [EE]  P=0, H=4 (mean P+H=6.2)
         "Reserves: Tap, Pay X build points -> Put 2 damage counters on Tem. Then choose o..."
Cost  4: Tion Medon (A) [FOTR]  P=1, H=3 (mean P+H=6.2)
         "[tap] -> Reveal a partially built card in your opponent's build zone. Remove one..."
Cost  4: Gungan Sapper [ION]  P=1, H=3 (mean P+H=6.2)
         "[tap] -> Choose a Gungan unit. Tap or untap that unit. Play only when no unit is..."
Cost  4: Anakin's Spirit (C) [LEG]  P=0, H=4 (mean P+H=6.2)
         "Anakin's Spirit doesn't count toward arena control. | Prevent all damage to and ..."
Cost  4: Luke Skywalker (R2) [OBWN]  P=1, H=3 (mean P+H=6.2)
         "Whenever a Tatooine Location is completed, gain 4 Force. | Reserves: [Tap] -> Re..."
Cost  4: Luke Skywalker (R2) (Promo) [OBWN]  P=1, H=3 (mean P+H=6.2)
         "Whenever a Tatooine Location is completed, gain 4 Force. | Reserves: [Tap] -> Re..."
Cost  4: Rune Haako (A) [PM]  P=2, H=2 (mean P+H=6.2)
         "Pay 0 Force -> Retreat Rune. | [tap] -> Draw 2 cards, then discard 2 cards from ..."
Cost  4: Sleen [RAS]  P=2, H=2 (mean P+H=6.2)
         "[tap] -> Your opponent puts the top card of his or her deck into his or her disc..."
Cost  4: Tynnra Pamla (A) [RO]  P=1, H=3 (mean P+H=6.2)
         "Reserves: Tap -> Choose the Space or Ground arena. Retreat up to 2 of your Rebel..."
Cost  4: Chancellor Tarsus Valorum (A) [RO2]  P=2, H=2 (mean P+H=6.2)
         "As long as you have 2 or more Jedi Masters in the Character arena, Tarsus can't ..."
Cost  4: Hardin (A) [RO2]  P=2, H=2 (mean P+H=6.2)
         "When Hardin is discarded from the Character arena, you may gain control of a Cha..."
Cost  4: Chief Chirpa (A) [ROTJ]  P=1, H=3 (mean P+H=6.2)
         "[tap] -> Gain 1 build point and 1 Force. Play only during your build step. | As ..."
Cost  4: R4-P17 (A) [ROTS]  P=1, H=3 (mean P+H=6.2)
         "[tap] -> Choose one: gain 1 build point, or remove up to 2 damage counters from ..."
Cost  4: Nute Gunray (D) [ROTS]  P=1, H=3 (mean P+H=6.2)
         "[tap], Pay 2 build points -> Look at your opponent's hand. You may choose and di..."
Cost  4: Garindan (B) [SAV]  P=2, H=2 (mean P+H=6.2)
         "Stealth | Each of your Stormtroopers gets +10 speed."
Cost  4: C1-10P (B) [SOR]  P=2, H=2 (mean P+H=6.2)
         "Stack: Ezra Bridger | When the battle step starts, choose one: C1-10P gets +20 s..."
Cost  4: H2 (A) [TDT]  P=1, H=3 (mean P+H=6.2)
         "Upkeep: Discard a card from your hand or tap H2. | As long as Ember Chankeli or ..."
Cost  4: Lieutenant Gregg (A) [TDT]  P=1, H=3 (mean P+H=6.2)
         "Upkeep: Discard a card from your hand or tap Gregg. | As long as Darth Vader is ..."
Cost  4: Tungo Li (A) [TDT]  P=1, H=3 (mean P+H=6.2)
         "Reserves: Tap -> Choose one: Your opponent discard a card from his or her hand. ..."
Cost  4: Maz Kanata (A) [TFA]  P=1, H=3 (mean P+H=6.2)
         "Reserves: Tap -> Search your deck and your discard pile for a Lightsaber Weapon ..."
Cost  4: B-U4D (A) [TFA]  P=0, H=4 (mean P+H=6.2)
         "When you deploy B-U4D, you may remove 1 damage counter from one of your Starfigh..."
Cost  4: R2-D2 (Q) [TFA]  P=1, H=3 (mean P+H=6.2)
         "Reserves: Tap -> Choose one: Gain 1 Force. Or:  Reveal a Luke Skywalker unit car..."
Cost  4: Maz Kanata (A) (LEGO) [TFA]  P=1, H=3 (mean P+H=6.2)
         "Reserves: Tap -> Search your deck and your discard pile for a Lightsaber Weapon ..."
Cost  4: Alcida-Auka (A) [TLJ]  P=1, H=3 (mean P+H=6.2)
         "Parry 1 | Each of your Caretakers costs 1 less build counter to deploy."
Cost  4: BB-9E (A) [TLJ]  P=1, H=3 (mean P+H=6.2)
         "Stealth | Each of your opponent's Characters loses Stealth. | Tap -> One of your..."
Cost  4: General Leia Organa Solo (A2) [TLJ]  P=1, H=3 (mean P+H=6.2)
         "INSERT: Fortitude (Leia can prevent unpreventable damage to herself.) | INSERT: ..."
Cost  4: BB-8 (D) [TLJ]  P=1, H=3 (mean P+H=6.2)
         "Starfighter Pilot. The Starfighter gets:  -This unit can have up to 2 Pilots.  -..."
Cost  4: General Leia Organa Solo (A2) (Promo) [TLJ]  P=1, H=3 (mean P+H=6.2)
         "INSERT: Fortitude (Leia can prevent unpreventable damage to herself.) | INSERT: ..."
Cost  4: Grogu (B) [TM]  P=0, H=4 (mean P+H=6.2)
         "Alternative Cost: Pay 4 Force | Parry 2 | INSERT: Pay 2 Force -> Protect 3"
Cost  4: Arvala Jawa Traders [TM]  P=1, H=3 (mean P+H=6.2)
         "Tap, Remove an Equipment card with printed build cost X from your hand from the ..."
Cost  4: General Valin Hess (A) [TMW]  P=3, H=1 (mean P+H=6.2)
         "Each of your opponent's units get Fury 1 | Put 1 damage counter each on two of y..."
Cost  4: Dock Worker [TMW]  P=1, H=3 (mean P+H=6.2)
         "Whenever your opponent attacks one of your Space units from another arena you ma..."
Cost  4: Han's Memory (A) [TROS]  P=0, H=4 (mean P+H=6.2)
         "Han's Memory doesn't count toward controlling any arena. | Prevent all damage to..."
Cost  4: Rey's Dark Vision (A) [TROS]  P=0, H=4 (mean P+H=6.2)
         "Rey's Dark Vision doesn't count toward controlling any arena. | Prevent all dama..."
Cost  4: Ahch-To Porgs [TROS]  P=0, H=4 (mean P+H=6.2)
         "When you deploy this unit to any arena, choose one: Remove 1 damage counter from..."
Cost  4: Elegos A'Kla (A) [VP]  P=0, H=4 (mean P+H=6.2)
         "Each unit (yours and your opponent's) in the Character arena gets "Whenever this..."
Cost  4: T0-B1 (A) [VV1]  P=2, H=2 (mean P+H=6.2)
         "Upkeep: Put 1 mastery counter on T0-B1 | Deploy: Search your deck for a Location..."
Cost  5: Nala Se (A) [AGD]  P=0, H=2 (mean P+H=7.8)
         "Reserves: Tap -> Remove 1 damage counter from each of your Clones in the Charact..."
Cost  5: Obi-Wan's Spirit (B) [ER]  P=0, H=2 (mean P+H=7.8)
         "Obi-Wan's Spirit doesn't count toward controlling the Character arena. | Prevent..."
Cost  5: Obi-Wan's Spirit (A) [ESB]  P=0, H=2 (mean P+H=7.8)
         "Obi Wan's Spirit doesn't count towards controlling the Character arena. | Preven..."
Cost  5: Qui-Gon's Spirit (A) [FOTR]  P=0, H=2 (mean P+H=7.8)
         "Qui-Gon's Spirit doesn't count towards controlling the Character arena. | Preven..."
Cost  5: Marka Ragnos's Spirit (B) [JK]  P=0, H=2 (mean P+H=7.8)
         "Marka Ragnos's Spirit doesn't count toward controlling the Character arena. | Pr..."
Cost  5: Qu Rahn's Spirit (A) [JK]  P=0, H=2 (mean P+H=7.8)
         "Qu Rahn's Spirit doesn't count toward controlling the Character arena. | Prevent..."
Cost  5: Marka Ragnos's Spirit (A) [TAL]  P=0, H=2 (mean P+H=7.8)
         "Marka Ragnos's Spirit doesn't count toward controlling the Character arena. | Pr..."
Cost  5: Freedon Nadd's Spirit (A) [TAL]  P=0, H=2 (mean P+H=7.8)
         "Freedon Nadd's Spirit doesn't count toward controlling the Character arena. | Pr..."
Cost  5: Karness's Spirit (A) [TDT]  P=0, H=3 (mean P+H=7.8)
         "Karness's Spirit doesn't count toward controlling the Character arena. | Prevent..."
Cost  5: Yoda's Spirit (B) [TLJ]  P=0, H=3 (mean P+H=7.8)
         "Yoda's Spirit doesn't count toward controlling the Character arena. | Prevent al..."
Cost  5: Luke's Spirit (A) [TROS]  P=0, H=3 (mean P+H=7.8)
         "Upkeep: Gain 1 Force | Luke's Spirit doesn't count towards controlling any arena..."
Cost  5: Father (A) [AGD]  P=0, H=4 (mean P+H=7.8)
         "Father doesn't count toward controlling the Character arena.  | Prevent all dama..."
Cost  5: Son (A) [AGD]  P=0, H=4 (mean P+H=7.8)
         "Son doesn't count toward controlling the Character arena. | Prevent all damage t..."
Cost  5: Jedi Spirits (B) [BAE]  P=0, H=4 (mean P+H=7.8)
         "Stack: Any Jedi Spirit. | Jedi Spirits doesn't count toward controlling any aren..."
Cost  5: Po Nudo (A) [FOTR]  P=1, H=3 (mean P+H=7.8)
         "[tap] -> Choose an arena. Remove one damage counter from each of your damaged Se..."
Cost  5: Chancellor Finis Valorum (A) [ION]  P=1, H=3 (mean P+H=7.8)
         "As long as Valorum is being attacked, Intercept abilities can't be activated. | ..."
Cost  5: Rune Haako (B) [ION]  P=2, H=2 (mean P+H=7.8)
         "When the roll for build points is made, if you have another Trade Federation Dip..."
Cost  5: Aks Moe (A) [ION]  P=2, H=2 (mean P+H=7.8)
         "Whenever a disrupt effect is played, draw a card."
Cost  5: Captain Daultay Dofine (A) [ION]  P=2, H=2 (mean P+H=7.8)
         "[Pilot] Capital Ship and Fleet Pilot. The Capital Ship or Fleet gets: * Upkeep: ..."
Cost  5: Ann and Tann Gella (A) [PM]  P=2, H=2 (mean P+H=7.8)
         "Each of your opponent's Characters gets -2 power. | [tap] -> One of your Charact..."
Cost  5: Nute Gunray (C) [PM]  P=2, H=2 (mean P+H=7.8)
         "Each of your other Trade Federation units costs 1 fewer build point to deploy an..."
Cost  5: Angel [AGD]  P=0, H=5 (mean P+H=7.8)
         "Your opponent can't attack this unit unless he or she pays 4 Force. | Whenever o..."
Cost  5: Force Priestesses (A) [BL]  P=0, H=5 (mean P+H=7.8)
         "Force Priestesses doesn't count toward controlling the Ground or Character arena..."
Cost  5: Nala Se (B) [BL]  P=1, H=4 (mean P+H=7.8)
         "Whenever one of your Clone Characters would be damaged, prevent 1 of that damage..."
Cost  5: King Ramsis Dendup (A) [BL]  P=2, H=3 (mean P+H=7.8)
         "When you deploy Ramsis, you may pay 2 build points. If you do, take 1 50/3/3 Ond..."
Cost  5: Grogu (I) [BOBF]  P=0, H=5 (mean P+H=7.8)
         "[Tap], Pay 2 Force -> Tap one of your opponent's Ground units or Characters. Pla..."
Cost  5: Separatist Mutant Horde [CWSO]  P=3, H=2 (mean P+H=7.8)
         "Fury 3 | Discard this unit from this arena -> Put 2 damage counters on one of yo..."
Cost  5: Lucien Draay (C) [DAN]  P=0, H=5 (mean P+H=7.8)
         "INSERT: Forewarning: Prevent up to 4 damage to Lucien and gain 1 Force. (Wheneve..."
Cost  5: Chancellor Palpatine (F) [FOTR]  P=2, H=3 (mean P+H=7.8)
         "Whenever the cost of a Diplomat's activated ability is paid, roll a die. If the ..."
Cost  5: Sly Moore (A) [FOTR]  P=2, H=3 (mean P+H=7.8)
         "[tap] -> Tap one of your opponent's Diplomats. Play only during your build step...."
Cost  5: Nute Gunray (E) [ION]  P=3, H=2 (mean P+H=7.8)
         "Each of your Trade Federation units gets "[tap], Pay 1 build point -> This unit ..."
Cost  5: Senator Palpatine (J) [ION]  P=1, H=4 (mean P+H=7.8)
         "When your opponent's build step starts, you may tap Palpatine. If you do, each o..."
Cost  5: Yaddle (A) [PM]  P=2, H=3 (mean P+H=7.8)
         "[tap] -> Draw 2 cards, then discard 1 card from your hand. Play only during your..."
Cost  5: Bail Organa (B) [ROTS]  P=2, H=3 (mean P+H=7.8)
         "Pay 2 build points, [tap] -> Tap one of your opponents units. Play only during y..."
Cost  5: Meekerdin-maa (A) [TDT]  P=2, H=3 (mean P+H=7.8)
         "When you deploy Meekerdin-maa, you may remove up to 2 damage counters from one o..."
Cost  5: Slicer [TEN]  P=1, H=4 (mean P+H=7.8)
         "Tap -> Search your deck for a non-unit card, show it to your opponent, and put i..."
Cost  5: Grogu (A) [TM]  P=0, H=5 (mean P+H=7.8)
         "Grogu can have up to 5 cards in his stack. | As long as you have Din Djarin in t..."
Cost  5: The Child (A) (Promo) [TM]  P=0, H=5 (mean P+H=7.8)
         "The Child can have up to 5 cards in his stack. | As long as you have The Mandalo..."
Cost  5: Grogu (F) [TMW]  P=0, H=5 (mean P+H=7.8)
         "Foresight: Gain 3 Force. | Pay 1 Force -> Absorb 2 | Pay 5 Force -> Meditate | I..."
Cost  5: Gideon's Lieutenant (A) [TMW]  P=2, H=3 (mean P+H=7.8)
         "This unit costs 1 less build counter to deploy  for each arena in which you don..."
Cost  6: Duchess Satine Kryze (B) [AGD]  P=0, H=4 (mean P+H=9.3)
         "When you deploy Satine, you may tap one of your other Mandalorians in the Charac..."
Cost  6: Nute Gunray (F) [AGD]  P=1, H=3 (mean P+H=9.3)
         "Each of your Trade Federation Droids gets +1 power | Tap, Pay 1 build point -> T..."
Cost  6: Sun Fac (B) [JG]  P=2, H=2 (mean P+H=9.3)
         "Reserves: Tap -> Show a face-down Geonosian card in your build zone to your oppo..."
Cost  6: Stormtrooper TK-622 [TDT]  P=2, H=2 (mean P+H=9.3)
         "Critical Hit 2 | Armor | This unit gets +2 power for each Rebel your opponent ha..."
Cost  6: Maz Kanata (B) [TFA]  P=1, H=3 (mean P+H=9.3)
         "Reserves: Tap -> Each of your unit's activated abilities costs 1 less Force to p..."
Cost  6: Luke's Illusion (B) [ALTA]  P=0, H=5 (mean P+H=9.3)
         "Treat Luke's Illusion as Luke Skywalker. | Luke's Illusion can't attack. | Each ..."
Cost  6: Luke's Illusion (B) (Promo) [ALTA]  P=0, H=5 (mean P+H=9.3)
         "Treat Luke's Illusion as Luke Skywalker. | Luke's Illusion can't attack. | Each ..."
Cost  6: Yoda (Q) [BL]  P=0, H=5 (mean P+H=9.3)
         "Tap -> Until next turn, win the game each player cannot. Only when the turn star..."
Cost  6: Nakha Urus (A) [AGD]  P=3, H=3 (mean P+H=9.3)
         "Nakha can't retreat | When you deploy Nakha, you may discard X cards from your h..."
Cost  6: Onaconda Farr (A) [AGD]  P=3, H=3 (mean P+H=9.3)
         "Each of your Rodians costs 1 less build counter to deploy. | As long as you have..."
Cost  6: Jocasta Nu (B) [AGD]  P=2, H=4 (mean P+H=9.3)
         "Reserves: Tap -> Draw a card and gain 1 Force. | Pay 1 Force -> Evade 1"
Cost  6: Poggle the Lesser (B) [AGD]  P=3, H=3 (mean P+H=9.3)
         "Each of your Geonosian Ground and Character units costs 1 less build counter to ..."
Cost  6: Jocasta Nu (B) (Promo) [AGD]  P=2, H=4 (mean P+H=9.3)
         "Reserves: Tap -> Draw a card and gain 1 Force. | Pay 1 Force -> Evade 1"
Cost  6: Jocasta Nu (B) (Promo-Film) [AGD]  P=2, H=4 (mean P+H=9.3)
         "Reserves: Tap -> Draw a card and gain 1 Force. | Pay 1 Force -> Evade 1"
Cost  6: Admiral Tarkin (F) [BL]  P=2, H=4 (mean P+H=9.3)
         "Each of your Clones costs 1 less build counter to deploy. | Pay 1 build point ->..."
Cost  6: General Maximilian Veers (C) [BOH]  P=3, H=3 (mean P+H=9.3)
         "When you deploy Veers, search your deck. You may take a Walker card from your de..."
Cost  6: Elite Gunship Pilot [CAD]  P=3, H=3 (mean P+H=9.3)
         "Gunship Pilot. The Gunship gets:  - Accuracy 1  - Critical Hit 1  - Elude  - Luc..."
Cost  6: Gorman "Camper" Vandrayk (A) [DAN]  P=2, H=4 (mean P+H=9.3)
         "Reserves: Tap -> Reveal a partially built Transport unit card in your build zone..."
Cost  6: Mon Mothma (F) [FOR]  P=3, H=3 (mean P+H=9.3)
         "Inspiration | As long as you have another Rebel in this arena, Mon Mothma gets S..."
Cost  6: Seelah Korsin (A) [TAL]  P=3, H=3 (mean P+H=9.3)
         "Critical Hit 2 | Stealth | When Seelah is discarded from the Character arena, ta..."
Cost  6: Ko Vakier (A) [TDT]  P=3, H=3 (mean P+H=9.3)
         "Transport Pilot. The Transport gets:  - +2 power  - Elude  - This unit can have ..."
Cost  6: Bala-Tik (A) [TFA]  P=3, H=3 (mean P+H=9.3)
         "Each of your opponent's Characters loses Bounty. | When you deploy Bala-Tik, tak..."
Cost  6: Commander Larma D'Acy (A) [TLJ]  P=3, H=3 (mean P+H=9.3)
         "As long as you have a Fortification or Location in the Space or Ground arena, ea..."
Cost  6: Baron Yasto Attsmun (A) [TLJ]  P=2, H=4 (mean P+H=9.3)
         "When you deploy Yasto, you may search your deck for an Undisputed Victor unit ca..."
Cost  6: Captain Mar Tuuk (A) [AGD]  P=2, H=5 (mean P+H=9.3)
         "Capital Ship and Fleet Pilot. The Capital Ship or Fleet gets:  - When the Space ..."
Cost  6: Ima-Gun Di (A) [AGD]  P=4, H=3 (mean P+H=9.3)
         "Inspiration | Tap -> Search your deck or discard pile for up to 2 Clone or Twi'l..."
Cost  6: Mother Talzin (A) [AGD]  P=3, H=4 (mean P+H=9.3)
         "Tap, Pay 1 build point -> Take 1 Subordinate with the Nightsister or Nightbrothe..."
Cost  6: Osi Sobeck (A) [AGD]  P=4, H=3 (mean P+H=9.3)
         "Tap, Pay 2 build points -> Take 1 50/4/2 Elite STAP Squad Subordinate with "Accu..."
Cost  6: Admiral Trench (B) [BL]  P=3, H=4 (mean P+H=9.3)
         "Whenever you deploy a Separatist Transport, you may pay 2 build points. If you d..."
Cost  6: Chancellor Palpatine (P) [BL]  P=3, H=4 (mean P+H=9.3)
         "Whenever you deploy a Diplomat to the Character arena, you may discard a card fr..."
Cost  6: Darts D'Nar (A) [BL]  P=3, H=4 (mean P+H=9.3)
         "When you deploy Darts, take 1 30/2/3 Zygerrian Slaver Subordinate with "Tap, Dis..."
Cost  6: Kaydel Ko Connix (B) [BOC]  P=3, H=4 (mean P+H=9.3)
         "When you deploy Kaydel, take 1 20/2/2 Crait Comms Soldier Subordinate with "Resi..."
Cost  6: Vober Dand (A) [BOSB]  P=3, H=4 (mean P+H=9.3)
         "Reserves: Tap, Return one of your Resistance Space unit cards from your discard ..."
Cost  6: Commander Bly (B) [CAD]  P=3, H=4 (mean P+H=9.3)
         "Armor | As long as you have Aayla Secura in any arena, Bly gets +2 power and Cri..."
Cost  6: Q'Anilia (A) [DAN]  P=1, H=6 (mean P+H=9.3)
         "Foresight: Look at the top 5 cards of any player's deck. Discard up to X of thos..."
Cost  6: Xamar (A) [DAN]  P=2, H=5 (mean P+H=9.3)
         "Foresight: Gain 1 Force. | Forewarning: Gain 1 Force. (Whenever Xamar is attacke..."
Cost  6: Jar Jar Binks (D) [ION]  P=3, H=4 (mean P+H=9.3)
         "Accuracy -1 | Lucky 2 | At the start of the battle step you may choose one of yo..."
Cost  6: Jedi Shadow [JEDI]  P=3, H=4 (mean P+H=9.3)
         "Switch: Precision/+1 power | Stealth | This unit gets Critical Hit 3 when attack..."
Cost  6: Mij Gilamar (A) [MAND]  P=2, H=5 (mean P+H=9.3)
         "Armor | When Mij would attack, remove 1 damage counter from each of your damaged..."
Cost  6: Mirta Gev (A) [MAND]  P=3, H=4 (mean P+H=9.3)
         "Fury 2 | Armor | Double Strike | When the defending unit is discarded as a resul..."
Cost  6: Bib Fortuna (A) [ROTJ]  P=3, H=4 (mean P+H=9.3)
         "Pay 0 Force -> Choose one of your neutral units in any arena. Put that unit face..."
Cost  6: Jocasta Nu (A) [SR]  P=2, H=5 (mean P+H=9.3)
         "As long as Jocasta is in the Character arena, draw 2 extra cards during your dra..."
Cost  6: Armand Isard (A) [TDT]  P=3, H=4 (mean P+H=9.3)
         "Stack: Ysanne Isard. | When you deploy Armand, you may pay 1 build point. If you..."
Cost  6: Bail Organa (C) [TDT]  P=2, H=5 (mean P+H=9.3)
         "When your build step starts, you may search your deck for a Diplomat unit card. ..."
Cost  6: Bail Organa (C) (Promo) [TDT]  P=2, H=5 (mean P+H=9.3)
         "When your build step starts, you may search your deck for a Diplomat unit card. ..."
Cost  6: Chancellor Lenever Villecham (A) [TFA]  P=3, H=4 (mean P+H=9.3)
         "Tap, Pay 3 Force -> Disrupt an attack. | Tap, Pay 3 Force -> Disrupt a Battle Ca..."
Cost  6: Rose Tico (D) [TLJ]  P=2, H=5 (mean P+H=9.3)
         "Rose costs 1 less build counter to deploy for each unique Resistance unit you ha..."
Cost  6: IG-11 (D) [TM]  P=2, H=5 (mean P+H=9.3)
         "Tap -> Choose one: Add 2 counters to your Resource. Play only during your build ..."
Cost  6: Emperor Palpatine (U) [TROS]  P=2, H=5 (mean P+H=9.3)
         "INSERT: Reserves: Tap -> Search your deck for a Space unit card, show it to your..."
Cost  6: Azlyn Rae (A) [UNION]  P=2, H=5 (mean P+H=9.3)
         "Upkeep: Put X damage counters on Azlyn, where X is the number of captivity count..."
Cost  6: Tulon Voidgazer (A) [VDR]  P=2, H=5 (mean P+H=9.3)
         "Upkeep: Put 1 damage counter on one of your Cyborgs in any arena or tap Voidgaze..."
Cost  6: Sith Master and Apprentice (O) [VV1]  P=1, H=6 (mean P+H=9.3)
         "Deploy: Put 2 corruption counters on one of your opponent's Jedi. | Foresight: D..."
Cost  7: Kal Skirata (A) [MAND]  P=1, H=1 (mean P+H=10.3)
         "Armor | As long as your opponent has 5 or more Character cards in his or her dis..."
Cost  7: King Katuunko (A) [AGD]  P=2, H=4 (mean P+H=10.3)
         "When you deploy Katuunko, take 1 40/2/2 Toydarian Royal Guard Subordinate with "..."
Cost  7: Bor Gullet [RO]  P=0, H=6 (mean P+H=10.3)
         "Upkeep: Look at your opponent's hand, and you may discard a card from his or her..."
Cost  7: Qui-Gon Jinn (I) [ALTA]  P=2, H=5 (mean P+H=10.3)
         "Qui-Gon gets +X power, where X is 7 minus the number of cards in your hand. | Di..."
Cost  7: Qui-Gon Jinn (I) (Promo) [ALTA]  P=2, H=5 (mean P+H=10.3)
         "Qui-Gon gets +X power, where X is 7 minus the number of cards in your hand. | Di..."
Cost  7: Kindalo [BL]  P=2, H=5 (mean P+H=10.3)
         "Switch: Shields 2/Damage Control 1 | When your build step starts, roll a die. If..."
Cost  7: Galen Erso (A) [RO]  P=2, H=5 (mean P+H=10.3)
         "Upkeep: Pay 1 build point or tap Galen. | When your build step starts, you may c..."
Cost  7: Admiral Ackbar (D) [TFA]  P=2, H=5 (mean P+H=10.3)
         "Each of your Resistance Space units gets +1 power and Critical Hit 1. | Tap -> C..."
Cost  7: Vice Admiral Amilyn Holdo (C) [TLJ]  P=2, H=5 (mean P+H=10.3)
         "Hidden Cost 4 | Tap -> Each of your Resistance Ground units and Characters costs..."
Cost  7: Pre Vizsla (A) [AGD]  P=2, H=6 (mean P+H=10.3)
         "Pre Vizsla gets +1 power for each Death Watch unit you have in the Character are..."
Cost  7: Stormtrooper Squad Leader [ANH]  P=4, H=4 (mean P+H=10.3)
         "Accuracy 1 | As long as this unit is in the Character arena, each of your other ..."
Cost  7: Ben Solo (E) [BAE]  P=4, H=4 (mean P+H=10.3)
         "Lucky 3 | Pay 1 Force -> Absorb 1 | Pay 1 Force -> Deflect 1 | Pay 1 Force -> Ev..."
Cost  7: Ben Solo (E) (Promo) [BAE]  P=4, H=4 (mean P+H=10.3)
         "Lucky 3 | Pay 1 Force -> Absorb 1 | Pay 1 Force -> Deflect 1 | Pay 1 Force -> Ev..."
Cost  7: Boba Fett (R) [BF]  P=4, H=4 (mean P+H=10.3)
         "INSERT: Slave I costs 1 less build counter to deploy. | [Pilot] Patrol Ship Pilo..."
Cost  7: Gregor (A) [BL]  P=4, H=4 (mean P+H=10.3)
         "Armor | Discard Gregor from the Character arena -> Prevent all damage to one of ..."
Cost  7: Captain Ackbar (E) [BL]  P=3, H=5 (mean P+H=10.3)
         "When you deploy Ackbar, take 2 50/1/2 Mon Calamari Warrior Subordinates with "Pa..."
Cost  7: Commander Cody (F) [BL]  P=4, H=4 (mean P+H=10.3)
         "Armor | When you deploy Cody, you may discard a card from your hand. If you do, ..."
Cost  7: Luke Skywalker (G2) [BOC]  P=0, H=8 (mean P+H=10.3)
         "When the battle phase starts, if Luke's Illusion is not in play, you may search ..."
Cost  7: Luke Skywalker (G2) (Promo) [BOC]  P=0, H=8 (mean P+H=10.3)
         "When the battle phase starts, if Luke's Illusion is not in play, you may search ..."
Cost  7: General Leia Organa Solo (W) [BOSB]  P=3, H=5 (mean P+H=10.3)
         "Forewarning: Gain 1 Force. | Parry 1 | When your build step starts, if you have ..."
Cost  7: Snoke (C) [BOSB]  P=4, H=4 (mean P+H=10.3)
         "Treat Snoke as a Dark Jedi Master. | Reserves: Tap -> Return a unit card from yo..."
Cost  7: Admiral Statura (C) [BOSB]  P=4, H=4 (mean P+H=10.3)
         "Reserves: Tap -> Move one of your Resistance Starfighters from your build zone t..."
Cost  7: B1 Patrol Droid Squad [CAD]  P=3, H=5 (mean P+H=10.3)
         "Treat this unit as a Separatist. | This unit costs 1 less build counter to deplo..."
Cost  7: Ennix Devian (A) [EE]  P=4, H=4 (mean P+H=10.3)
         "Inspiration | Each New Republic and Rebel gets -2 power when attacking Ennix."
Cost  7: Lando Calrissian (C) [ESB]  P=4, H=4 (mean P+H=10.3)
         "Discard one of your other units from any arena or your build zone -> Prevent all..."
Cost  7: Lando Calrissian (C) (Promo) [ESB]  P=4, H=4 (mean P+H=10.3)
         "Discard one of your other units from any arena or your build zone -> Prevent all..."
Cost  7: Grand Admiral Thrawn (G) [FOR]  P=4, H=4 (mean P+H=10.3)
         "Inspiration | Pay 3 Force -> Choose an arena and an expansion symbol. Each unit ..."
Cost  7: Grand Admiral Thrawn (G) (Promo) [FOR]  P=4, H=4 (mean P+H=10.3)
         "Inspiration | Pay 3 Force -> Choose an arena and an expansion symbol. Each unit ..."
Cost  7: Rav Bralor (A) [MAND]  P=2, H=6 (mean P+H=10.3)
         "Armor | As long as Rav is in the Character arena, each of your Mandalorian Space..."
Cost  7: General Davits Draven (A) [RO]  P=4, H=4 (mean P+H=10.3)
         "When you deploy Davits, you may discard a card from your hand. If you do, search..."
Cost  7: Captain Cassian Andor (B) [RO]  P=4, H=4 (mean P+H=10.3)
         "Fury 2 | Stealth | Tap -> Put 3 damage counters on a non-Sith Character. Play on..."
Cost  7: Baron Soontir Fel (B) [RS]  P=4, H=4 (mean P+H=10.3)
         "Accuracy 2 | Starfighter Pilot. The Starfighter gets: -Accuracy 2 -Critical Hit ..."
Cost  7: Han Solo (B2) [SOLO]  P=4, H=4 (mean P+H=10.3)
         "Lucky 2 | Transport Pilot. The Transport gets:  - +20 speed - Parry 1 - Pay 1 Fo..."
Cost  7: Alexsandr Kallus (A) [SOR]  P=4, H=4 (mean P+H=10.3)
         "Armor | Kallus gets +2 power when attacking a Rebel. | Each of your Imperials ge..."
Cost  7: Darth Sidious (B) [SR]  P=3, H=5 (mean P+H=10.3)
         "Pay 1 Force -> Evade 2 | Pay 4 Force, discard one of your other Characters from ..."
Cost  7: Biggs Darklighter (B) [TDT]  P=4, H=4 (mean P+H=10.3)
         "When you deploy Biggs, you may add or remove 1 captivity counter from a unit in ..."
Cost  7: Haka Hai (A) [TDT]  P=3, H=5 (mean P+H=10.3)
         "When you deploy Haka, take 1 50/3/2 Pirate Captain Subordinate with "Fury 2" and..."
Cost  7: Nera Dantels (A) [TDT]  P=3, H=5 (mean P+H=10.3)
         "Stealth | When you deploy Nera, take 1 40/3/3 Rebel Freighter Subordinate with "..."
Cost  7: Nosaurian Commander [TDT]  P=4, H=4 (mean P+H=10.3)
         "Each of your Nosaurians costs 1 less build counter to deploy. | Tap, Pay 1 build..."
Cost  7: Princess Leia (S) [TDT]  P=4, H=4 (mean P+H=10.3)
         "Leia can't retreat or pilot a unit as long as she has 1 or more captivity counte..."
Cost  7: Rianna Saren (A) [TDT]  P=4, H=4 (mean P+H=10.3)
         "Lucky 1 | When you deploy Rianna, take 1 60/2/2 Zeeo Subordinate with "Accuracy ..."
Cost  7: Dass Jennir (D) [TDT]  P=4, H=4 (mean P+H=10.3)
         "Stealth | Remove 1 captivity counter from one of your opponent's Space units -> ..."
Cost  7: Beyghor Sahdett (C) [TDT]  P=4, H=4 (mean P+H=10.3)
         "When your build step starts, choose one: Beyghor gets the Imperial Dark Jedi Mas..."
Cost  7: Biggs Darklighter (B) (Promo) [TDT]  P=4, H=4 (mean P+H=10.3)
         "When you deploy Biggs, you may add or remove 1 captivity counter from a unit in ..."
Cost  7: Princess Leia (S) (Promo) [TDT]  P=4, H=4 (mean P+H=10.3)
         "Leia can't retreat or pilot a unit as long as she has 1 or more captivity counte..."
Cost  7: Rianna Saren (A) (Promo) [TDT]  P=4, H=4 (mean P+H=10.3)
         "Lucky 1 | When you deploy Rianna, take 1 60/2/2 Zeeo Subordinate with "Accuracy ..."
Cost  7: Darth Tenebrous (A) [TEN]  P=3, H=5 (mean P+H=10.3)
         "Tap, Pay 5 Force -> Each of your Sith gets Critical Hit 1 and "This unit can't b..."
Cost  7: Admiral Statura (A) [TFA]  P=4, H=4 (mean P+H=10.3)
         "Each of your Resistance Space units gets Accuracy 1. | Tap, Tap one of your Resi..."
Cost  7: First Order Commander [TFA]  P=4, H=4 (mean P+H=10.3)
         "When you deploy this unit, you may look at your opponent's hand. | Each of your ..."
Cost  7: General Leia Organa Solo (Z) [TLJ]  P=2, H=6 (mean P+H=10.3)
         "Whenever one of your Resistance Space units would be damaged, prevent 1 of that ..."
Cost  7: Finn (H) [TLJ]  P=4, H=4 (mean P+H=10.3)
         "As long as you have a Thief in any arena, each of your Mission cards costs 1 les..."
Cost  7: Resistance High Command (B) [TROS]  P=4, H=4 (mean P+H=10.3)
         "Switch: Stealth/Pay 1 Force -> Redirect | Your Mission cards can't be disrupted...."
Cost  7: Jaina Solo (C) [VP]  P=4, H=4 (mean P+H=10.3)
         "Parry 2 | Pay 1 Force -> Evade 1 | Squadron and Starfighter Pilot. The Squadron ..."
Cost  7: Lar Le'Ung (A) [VP]  P=4, H=4 (mean P+H=10.3)
         "Lar can't use Evade to prevent damage from a Yuuzhan Vong. | Luke Skywalker can'..."
Cost  7: Karre (A) [VV1]  P=3, H=5 (mean P+H=10.3)
         "Forewarning: Gain 2 Force. | Pay X Force, up to 5 -> Karre gets +X-1 power until..."
Cost  8: Mon Mothma (A) [ROTJ]  P=1, H=4 (mean P+H=11.3)
         "[tap] -> Each of your Rebel units costs 1 fewer build counter to deploy. Play on..."
Cost  8: Admiral Raddus (A) [RO]  P=2, H=4 (mean P+H=11.3)
         "Each of your Rebel Space units gets +3 health."
Cost  8: Admiral Ackbar (A) [ROTJ]  P=2, H=5 (mean P+H=11.3)
         "Each of your Rebel Space units gets +3 power."
Cost  8: Baron Tarko (A) [TDT]  P=3, H=4 (mean P+H=11.3)
         "When you deploy Tarko, take 1 40/4/4 AT-MP Subordinate and put it into the Groun..."
Cost  8: Vice Admiral Amilyn Holdo (B) [TLJ]  P=2, H=5 (mean P+H=11.3)
         "Inspiration | Each of your Resistance Characters costs 1 less build counter to d..."
Cost  8: Alliance High Command (C) [ALTA]  P=4, H=4 (mean P+H=11.3)
         "Stack: Any unique Rebel Officer. | Alliance High Command can have up to 6 cards ..."
Cost  8: Nite Owls (A) [BL]  P=4, H=4 (mean P+H=11.3)
         "Switch: Double Strike/Accuracy 1 | Whenever Nite Owls is attacked, you may pay 3..."
Cost  8: Elite Galactic Marines (A) [CAD]  P=4, H=4 (mean P+H=11.3)
         "Switch: Double Strike / Elude | Accuracy 2"
Cost  8: Mutant Horde [CWSO]  P=4, H=4 (mean P+H=11.3)
         "Fury 2 | When this unit is discarded from any arena, you may pay 3 Force. If you..."
Cost  8: Orn Free Taa (A) [PM]  P=3, H=5 (mean P+H=11.3)
         "[tap], Pay 1 build point -> Choose one of your opponent's units. Tap that unit. ..."
Cost  8: Alliance High Command (B) [RO]  P=4, H=4 (mean P+H=11.3)
         "Stack: Any unique Rebel Officer. | Stealth | As long as you have at least 3 Rebe..."
Cost  8: Ryder Azadi (A) [SOR]  P=3, H=5 (mean P+H=11.3)
         "Inspiration | Each of your Lothal Rebel Characters costs 1 less build counter to..."
Cost  8: Beyghor Sahdett (A) [TDT]  P=4, H=4 (mean P+H=11.3)
         "Elude | Beyghor gets Accuracy 3 when attacking a non-unique unit. | Double Strik..."
Cost  8: General Leia Organa Solo (R) [TFA]  P=3, H=5 (mean P+H=11.3)
         "Inspiration | Tap -> Search your deck for a Han Solo unit card, show it to your ..."
Cost  8: Vice Admiral Amilyn Holdo (A) [TLJ]  P=3, H=5 (mean P+H=11.3)
         "Flagship Pilot. The Flagship gets:  -When your build step starts, choose one: Dr..."
Cost  8: Darth Malgus (D) [TOR]  P=1, H=7 (mean P+H=11.3)
         "Fury 3 | Malgus gets +1 power for each damage counter on him. | Pay 2 Force -> E..."
Cost  8: Cham Syndulla (A) [AGD]  P=5, H=4 (mean P+H=11.3)
         "Bounty: Take 1 50/4/3 Freedom Fighter Squad Subordinate with "Pay 0 Force -> Ret..."
Cost  8: Rey (E) [BOSB]  P=4, H=5 (mean P+H=11.3)
         "Stealth | As long as your Force total is 10 or more, Rey gets Focus 2, Damage Co..."
Cost  8: Super Battle Droid Sentry Guard [CAD]  P=5, H=4 (mean P+H=11.3)
         "Treat this unit as a Separatist Bodyguard. | Double Damage (Double the damage, a..."
Cost  8: Jarael (A) [DAN]  P=4, H=5 (mean P+H=11.3)
         "Critical Hit 1 | Double Damage | Stealth"
Cost  8: Luke Skywalker (J) [ESB]  P=5, H=4 (mean P+H=11.3)
         "Whenever you prevent damage to one of your units, draw a card. | Pay 4 Force -> ..."
Cost  8: Saw Gerrera (B) [RO]  P=4, H=5 (mean P+H=11.3)
         "Armor | Resilience 3 (As long as Saw has at least 3 damage counters on him, he g..."
Cost  8: Emperor Palpatine (C) [ROTJ]  P=3, H=6 (mean P+H=11.3)
         "[tap], Pay X Force -> Choose a unit in the Character arena. Emperor Palpatine do..."
Cost  8: L3-37 (B) [SOLO]  P=4, H=5 (mean P+H=11.3)
         "Armor | Inspiration | Tap a Droid in the Ground or Character arena -> Remove X c..."
Cost  8: Tobias Beckett (C) [SOLO]  P=4, H=5 (mean P+H=11.3)
         "Treat Beckett as an Imperial Officer. | As long as Beckett is the only Officer y..."
Cost  8: Captain Ozzik Sturn (A) [TDT]  P=4, H=5 (mean P+H=11.3)
         "Each of your Imperials gets +2 power and Stun 2 when attacking a Wookiee. | When..."
Cost  8: General Rahm Kota (B) [TDT]  P=4, H=5 (mean P+H=11.3)
         "Foresight: Put 2 captivity counters on a tapped Character. | Armor | When you de..."
Cost  8: Beyghor Sahdett (B) [TDT]  P=6, H=3 (mean P+H=11.3)
         "Elude | Parry 3 | Beyghor gets Critical Hit 4 when attacking a unique unit. | Pa..."
Cost  8: Elite First Order Squad [TFA]  P=4, H=5 (mean P+H=11.3)
         "Switch: Critical Hit 2/Accuracy 1 | As long as Captain Phasma or Kylo Ren is in ..."
Cost  8: Kanjiklub Gang (A) [TFA]  P=5, H=4 (mean P+H=11.3)
         "Bounty: Draw a card. | Fury 2 | Tap -> Discard the top 3 cards of your opponent'..."
Cost  8: Din Djarin (C) [TM]  P=4, H=5 (mean P+H=11.3)
         "Inspiration | Resilience 3 | INSERT: Pay 0 Force -> One of your other units in t..."
Cost  8: Nico Okarr (A) [TOR]  P=4, H=5 (mean P+H=11.3)
         "Accuracy 1 | Fury 1 | Double Strike"
Cost  8: Mara Jade Skywalker (I) [VP]  P=4, H=5 (mean P+H=11.3)
         "As long as Luke Skywalker is in any arena, Mara gets Double Damage and Damage Co..."
Cost  8: Mara Jade Skywalker (I) (Promo) [VP]  P=4, H=5 (mean P+H=11.3)
         "As long as Luke Skywalker is in any arena, Mara gets Double Damage and Damage Co..."
Cost  9: Droideka Squad [CAD]  P=4, H=4 (mean P+H=12.4)
         "Switch: +20 speed / Accuracy 1 | Treat this unit as a Separatist. | Shields 2 | ..."
Cost  9: Darth Maul (H) [ION]  P=4, H=4 (mean P+H=12.4)
         "Maul gets +10 speed, +1 power, and +1 health for each card stacked beneath him. ..."
Cost  9: Jahan Cross (A) [TDT]  P=4, H=4 (mean P+H=12.4)
         "Stealth | When you deploy Jahan,  you may shuffle your deck. If you do, take 1 6..."
Cost  9: Darth Sidious (I) [FOTR]  P=4, H=5 (mean P+H=12.4)
         "Pay 2 Force -> Evade 2 | [tap], Pay X Force -> Choose one of your opponent's Clo..."
Cost  9: Commander Thorn (A) [BL]  P=5, H=5 (mean P+H=12.4)
         "Switch: Inspiration/Accuracy 1 | Thorn gets +1 power for each damage counter on ..."
Cost  9: Saesee Tiin (B) [CWSO]  P=5, H=5 (mean P+H=12.4)
         "Switch: Armor / +30 speed, +1 power | Tap -> Choose one of your opponent's damag..."
Cost  9: T'ra Saa (A) [LEG]  P=3, H=7 (mean P+H=12.4)
         "Each of your Jedi gets "Adapt: Accuracy 1/ Fortitude/Shields 1" | Pay 0 Force ->..."
Cost  9: Raskta Lsu (A) [RO2]  P=5, H=5 (mean P+H=12.4)
         "Accuracy 1 | Critical Hit 2 | Parry 2 | You can attach Lightsaber Weapons to Ras..."
Cost  9: Han Solo (K) [ROTJ]  P=5, H=5 (mean P+H=12.4)
         "Accuracy 1 | Lucky 2 | Each of your other Rebel Ground units and Rebel Character..."
Cost  9: Anakin Solo (C) [SBS]  P=5, H=5 (mean P+H=12.4)
         "Inspiration | When you deploy Anakin, gain 1 Force. | When Anakin is discarded f..."
Cost  9: Anakin Solo (C) (Promo) [SBS]  P=5, H=5 (mean P+H=12.4)
         "Inspiration | When you deploy Anakin, gain 1 Force. | When Anakin is discarded f..."
Cost  9: Darth Tyranus (L) [SITH]  P=5, H=5 (mean P+H=12.4)
         "Whenever you play a Mission card, you may choose an arena. If you do, whenever o..."
Cost  9: Captain Tarpals (C) [TEN]  P=5, H=5 (mean P+H=12.4)
         "Switch: Inspiration/Accuracy 1 | Lucky 2 | Each of your Gungan Creatures gets +1..."
Cost  9: Poe Dameron (B) [TFA]  P=5, H=5 (mean P+H=12.4)
         "Switch: Inspiration/Accuracy 2 | Whenever Poe is damaged, you may search your de..."
Cost  9: The Armorer (B) [TM]  P=5, H=5 (mean P+H=12.4)
         "Switch: Riposte 3/Tap -> Protect 5 | Armor | Intimidation | Pay 1 Force -> Inter..."
Cost  9: Din Djarin (F) [TMW]  P=5, H=5 (mean P+H=12.4)
         "Ferocity | Armor | Whenever Din attacks, the defending unit loses Armor for that..."
Cost  9: Din Djarin (F) (Promo) [TMW]  P=5, H=5 (mean P+H=12.4)
         "Ferocity | Armor | Whenever Din attacks, the defending unit loses Armor for that..."
Cost  9: Ganner Rhysode (B) [TUF]  P=5, H=5 (mean P+H=12.4)
         "Intimidation (Ganner gets +10 speed, +1 power, and +1 health for each of your op..."
Cost  9: Shedao Shai (A) [VP]  P=5, H=5 (mean P+H=12.4)
         "When you deploy Shedao, take 1 40/4/4 Yuuzhan Vong Subaltern Subordinate with "F..."
Cost 10: Am (A) [VV1]  P=4, H=6 (mean P+H=13.4)
         "Double Strike | Overkill | Pay 3 Force -> Am gets Armor until end of turn. | Pay..."
Cost 10: Margrave Juro (A) [VV1]  P=6, H=5 (mean P+H=13.4)
         "Hidden Cost 8 | Deploy: When one of your opponent's units uses a Force-activated..."
Cost 10: Margrave Juro (A) (Promo) [VV1]  P=6, H=5 (mean P+H=13.4)
         "Hidden Cost 8 | Deploy: When one of your opponent's units uses a Force-activated..."
Cost 11: Bastila Shan (C) [KAE]  P=4, H=6 (mean P+H=14.1)
         "Each of your other Old Republic units gets Accuracy 1 and Lucky 1. | Double Stri..."
Cost 11: Bastila Shan (C) (Promo) [KAE]  P=4, H=6 (mean P+H=14.1)
         "Each of your other Old Republic units gets Accuracy 1 and Lucky 1. | Double Stri..."
Cost 12: General Grievous (K) [CAD]  P=4, H=8 (mean P+H=16.1)
         "Treat Grievous as a Dark Jedi Droid. | Armor | Damage Control 2 (When your build..."
Cost 12: Vandar Tokare (A) [DAN]  P=4, H=8 (mean P+H=16.1)
         "Forewarning: Gain 4 Force. (Whenever Vandar is attacked, you may predict the num..."
Cost 13: Darth Tyranus (O) [CAD]  P=4, H=9 (mean P+H=16.2)
         "Switch: Pay 2 Force -> Deflect 2 / Parry 4 | Inspiration | Whenever your opponen..."
Cost 13: General Weiss's AT-ST (A) [IA]  P=5, H=9 (mean P+H=16.2)
         "Armor | Whenever General Weiss's AT-ST attacks, choose one: Accuracy 1; Critical..."
```


## Mission (928 cards)

_Insufficient unit data for regression model._

**Keyword frequency by cost tier:**

```
Cost  0: Meditate (11%), Alternative Cost (3%), Enhance (3%), Lucky (3%), Focus (2%)
Cost  1: Meditate (15%), Enhance (4%), Deploy (4%), Alternative Cost (3%), Upkeep (2%)
Cost  2: Meditate (11%), Enhance (3%), Fury (3%), Deploy (3%), Critical Hit (2%)
Cost  3: Meditate (10%), Reduced Cost (6%), Avenge (3%), Upkeep (3%), Bounty (1%)
Cost  4: Meditate (7%), Bounty (5%), Accuracy (5%), Deploy (5%), Stack (5%)
Cost  5: Upkeep (7%), Overkill (7%), Fury (7%)
Cost  6: Pilot (14%)
```


## Resource (219 cards)

_Insufficient unit data for regression model._

**Keyword frequency by cost tier:**

```
Cost  0: Fury (12%)
Cost  2: Fury (12%), Bounty (8%), Upkeep (8%), Lucky (8%), Fortitude (4%)
Cost  3: Fury (11%), Accuracy (8%), Focus (7%), Lucky (5%), Deploy (5%)
Cost  4: Accuracy (10%), Deploy (8%), Critical Hit (7%), Bounty (7%), Evade (5%)
Cost  5: Critical Hit (10%), Inspiration (5%), Stack (5%), Resilience (5%), Accuracy (5%)
```


## Equipment (793 cards)

_Insufficient unit data for regression model._

**Keyword frequency by cost tier:**

```
Cost  0: Equip (97%), Foresight (8%), Critical Hit (8%), Accuracy (5%), Stun (5%)
Cost  1: Equip (80%), Critical Hit (11%), Lucky (5%), Accuracy (5%), Bounty (5%)
Cost  2: Equip (80%), Critical Hit (8%), Accuracy (5%), Upkeep (5%), Parry (5%)
Cost  3: Equip (79%), Critical Hit (16%), Inspiration (11%), Ferocity (11%), Accuracy (7%)
Cost  4: Equip (100%), Intimidation (33%)
```


## Location (568 cards)

_Insufficient unit data for regression model._

**Keyword frequency by cost tier:**

```
Cost  0: Critical Hit (14%), Bounty (14%), Overkill (7%), Elude (7%), Fury (7%)
Cost  1: Deploy (7%), Stealth (4%), Upkeep (3%), Alternative Cost (3%), Damage Control (2%)
Cost  2: Deploy (10%), Critical Hit (4%), Damage Control (3%), Bounty (3%), Accuracy (3%)
Cost  3: Deploy (16%), Damage Control (7%), Hidden Cost (6%), Lucky (6%), Backfire (4%)
Cost  4: Deploy (32%), Damage Control (14%), Reduced Cost (9%), Shields (9%), Accuracy (5%)
Cost  5: Deploy (57%), Forewarning (29%), Hidden Cost (14%), Upkeep (14%), Stack (14%)
```


## Battle (1 cards)

_Insufficient unit data for regression model._
