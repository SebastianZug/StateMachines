# StateMachines
Implementation of a traffic light based on D-Flip-Flops


                  .-.     .-.      .-.     .-.            
  Rot            ( X )   ( X )    (   )   (   )               
                  '-'     '-'      '-'     '-'
                  .-.     .-.      .-.     .-.            
  Gelb           (   )   ( X )    (   )   ( X )               
                  '-'     '-'      '-'     '-'
                  .-.     .-.      .-.     .-.            
  Grün           (   )   (   )    ( X )   (   )               
                  '-'     '-'      '-'     '-'
 
               --> 2s ---> 2s ---> 100s ---> 2s -|
               |                                 |
               -----------------------------------
                                                 


                   I      II       III     IV       Zustand
