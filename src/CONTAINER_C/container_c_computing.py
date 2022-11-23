
import numpy as np
import datetime

from container_c_data import DataModel


class ComputingModel(DataModel):
   
   # ********** step generators **********************

   def _gen_fuel_conv_step(self):
      n_isot = self.get_isot_count()
      A = [(2**i*[None], self.mat_lambda * self.dt/2**i + np.identity(n_isot)) for i in range(self.max_iter)]
      # ******* time 0 ***********************
      self.fuel_mol = F = self.isot_init_fuel_mol * (1 - self.isot_soluable_fuel_frac)
      F2 = np.empty(n_isot)
      yield True
      # ******* next times *******************
      while True:
         for n, a in A:
            F2[:] = F
            for _ in n:
               F2[:] = F2 @ a
               if F2.min() < 0.: break
            else: break
         else:
            print("\nFuel conversion numeric error")
            yield False
         F[:] = F2
         yield True


   def _gen_deg_conv_step(self):
      n_isot = self.get_isot_count()
      A = [(2**i*[None], self.mat_lambda * self.dt/2**i + np.identity(n_isot)) for i in range(self.max_iter)]
      # ******* time 0 ***********************
      self.deg_ratio = self.soluable_frac
      self.deg_mol = D = self.isot_init_fuel_mol * self.isot_soluable_fuel_frac
      D2 = np.empty(n_isot)
      yield True
      # ******* next times *******************
      while True:
         for n, a in A:
            D2[:] = D
            for _ in n:
               D2[:] = D2 @ a
               if D2.min() < 0.: break
            else: break
         else:
            print("\nDegradation conversion numeric error")
            yield False
         D[:] = D2
         yield True


   def _gen_others_conv_step(self):
      n_isot, n_lay = self.get_isot_count(), self.get_bent_lay_count()
      A = [(2**i*[None], self.mat_lambda * self.dt/2**i + np.identity(n_isot)) for i in range(self.max_iter)]
      # ******* time 0 ******************
      M = np.zeros((1 + 2*n_lay + 1, n_isot))
      M2 = np.empty((1 + 2*n_lay + 1, n_isot))
      self.w_mol = M[:n_lay+1]
      self.bent_lay_r_mol = M[(n_lay+1):-1]
      self.granit_mol = M[-1]
      self.granit_cumsum_mol = np.zeros(n_isot)
      self.cont_w_mol = self.w_mol[0]
      self.bent_lay_w_mol = self.w_mol[1:]
      yield True
      # ******* next times **************
      while True:
         for n, a in A:
            M2[:] = M
            for _ in n:
               M2[:] = M2 @ a
               if M2.min() < 0.: break
            else: break
         else:
            print("\nOther conversion numeric error")
            yield False
         M[:] = M2
         yield True


   def _gen_cont_direct_outflow_step(self):
      C, G = self.cont_w_mol, self.granit_mol
      r = 1 - np.exp( - self.cont_w_direct_outflow_rate * self.dt)
      Delta = np.empty(self.get_isot_count())
      while True:
         Delta[:] = C * r
         C[:] -= Delta
         G[:] += Delta
         yield


   def _gen_set_bent_volume_and_porosity_step(self):
      # ********* constants **********************
      n_lay = self.get_bent_lay_count()
      B_geom_V = self.bent_lay_geom_V
      self.bent_lay_porosity = P = np.empty((n_lay, 1))
      # ********* water volumes ***********************
      self.w_m3 = np.empty((1 + n_lay, 1))
      self.cont_w_m3 = self.w_m3[0]
      self.bent_lay_w_m3 = B_water_V = self.w_m3[1:]
      self.cont_w_m3[:] = self.cont_water_V_0
      # *****************************************
      while True:
         P[:] = next(self.fcn_bent_lay_mod_porosity)
         B_water_V[:] = P * B_geom_V
         yield


   def _gen_diffusion_and_sorption_step(self):
       # *********** first time ***********************
      yield True
      # ************ constants *******************     
      n_lay, n_isot, dt = self.get_bent_lay_count(), self.get_isot_count(), self.dt
      dt_steps = [(2**i*[None], dt/2**i) for i in range(self.max_iter)]
      B_diff = - 2 * np.pi * self.isot_bent_D_ef_m2_s * self.year_seconds / np.log(self.bent_lay_r / (self.bent_lay_r - self.bent_dr)) * self.cont_h
      bound_conc_0 = self.bent_bound_conc_0
      G_diff = - 2 * np.pi * self.isot_granit_D_ef_m2_s * self.year_seconds / np.log(1 + self.granit_width / self.bent_lay_r[-1]) * self.cont_h * (self.granit_c_rate - 1)
      Kd_density = self.isot_bent_Kd * self.bent_density
      # ************* references **************************
      porosity, A = self.bent_lay_porosity, np.empty((n_lay, n_isot))
      B_diff_m, B_diff_m_dt = np.empty((n_lay, n_isot)), np.empty((n_lay, n_isot))
      G_diff_dt = np.empty(n_isot)
      C, B, R = self.cont_w_mol, self.bent_lay_w_mol, self.bent_lay_r_mol
      V = self.w_m3
      conc = np.empty((1 + n_lay, n_isot))
      CB2 = np.empty((1 + n_lay, n_isot))
      B_plus = np.empty((n_lay, n_isot))      
      G_plus, G_all_plus = np.empty(n_isot), np.empty(n_isot)
      # ************** next steps **********************
      while True:
         area_frac = next(self.fcn_contact_area)
         B_diff_m[:] = B_diff * next(self.fcn_bent_lay_mod_D_ef)
         for n, iter_dt in dt_steps:
            B_diff_m_dt[:] = B_diff_m * iter_dt
            G_diff_dt[:] = G_diff * iter_dt
            CB2[:], G_all_plus[:] = self.w_mol, 0
            for _ in n:
               conc[:] = CB2 / V
               conc[0] *= area_frac
               B_plus[:] = B_diff_m_dt * (conc[1:] - conc[:-1])
               CB2[1:] += B_plus
               CB2[:-1] -= B_plus
               if bound_conc_0:
                 G_all_plus[:] += CB2[-1]
                 CB2[-1] = 0.
               else:
                 G_plus[:] = G_diff_dt * conc[-1]
                 G_all_plus[:] += G_plus
                 CB2[-1] -= G_plus               
               if CB2.min() < 0.: break
            else: break
         else:
            print("\nDiffusion numeric error")
            yield False
         A[:] = Kd_density / porosity * next(self.fcn_bent_lay_mod_Kd)
         C[:], B[:] = CB2[0], (R + CB2[1:]) / (1 + A)
         R[:] = B * A
         self.granit_mol[:] += G_all_plus
         self.granit_cumsum_mol[:] += G_all_plus
         yield True


   def _gen_deg_fuel_step(self):
      n_isot = self.get_isot_count()
      F_all = np.sum(self.isot_init_fuel_mol)
      F, DEG = self.fuel_mol, self.deg_mol
      # ********** first time *************************
      D_plus = np.zeros(n_isot)
      self.deg_ratio = D1 = next(self.fcn_deg)
      yield
      # ********** next times **********************
      while D1 < 1.:
         D2 = next(self.fcn_deg)
         D_plus[:] = (D2 - D1) * F_all / np.sum(F) * F
         F[:] -= D_plus
         DEG[:] += D_plus
         self.deg_ratio = D1 = D2
         yield
      

   def _gen_dissolve_step(self):
      cont_V = self.cont_w_m3[0]
      isot_1 = slice(0, len([None for i in self.elem_isotopes if type(i) == int]))
      cmax_isot_1 = self.elem_c_max[isot_1]
      DEG, W = self.deg_mol[isot_1], self.cont_w_mol[isot_1]
      D, B = np.empty(len(W)), np.empty(len(W), "bool")
      cmax_isot_n = [(self.elem_c_max[i], isots) for i, isots in enumerate(self.elem_isotopes) if type(isots)==slice]
      p_deg, p_w = self.deg_mol, self.cont_w_mol
      sum_all_fuel_mol = np.sum(self.isot_init_fuel_mol)
      sum_dissolve_mol = 0
      while True:
         # ******* 1 isotope per element ***************************
         D[:] = cmax_isot_1 * cont_V - W
         B[:] = D > DEG
         D[B] = DEG[B]
         B[:] = D < 0
         D[B] = 0.
         W += D
         DEG -= D
         sum_dissolve_mol += np.sum(D)
         # ********* n isotopes per element  ***************
         for c_max, i in cmax_isot_n:
            delta, deg = c_max * cont_V - np.sum(p_w[i]), np.sum(p_deg[i])
            if delta > deg: 
               sum_dissolve_mol += deg
               p_w[i] += p_deg[i]
               p_deg[i] = 0.
            elif delta > 0.:
               sum_dissolve_mol += delta
               p_delta = delta * p_deg[i] / deg
               p_w[i] += p_delta
               p_deg[i] -= p_delta
         self.dissolved_ratio = sum_dissolve_mol / sum_all_fuel_mol
         yield


   # ********* main computation ************************

   def compute(self):
      print("Preparing data for computing ...")

      # ****** create variables *******************
      dt = self.dt
      sim_t_n = self.sim_t_n
      out_t_n_step = self.out_t_n_step
      T_i_w = self.T_i_water_inflow
      out_model = self.out_model
      proc_t_n_step = sim_t_n // 100

      # ************ initial time index *****************
      t_i = 0
      start_calc_time = datetime.datetime.now()

      # ******* steps calculation ******************************
      #  *** every next() computes result for time index t_i ***

      print("Computing results for times ...")

      # *********** before water inflow **************
      fuel_conv_step = self._gen_fuel_conv_step()
      deg_conv_step = self._gen_deg_conv_step()
      if T_i_w > 0: 
         print("\tBefore water inflow ...")
         while t_i < T_i_w and t_i <= sim_t_n:
            if not next(fuel_conv_step): return False
            if not next(deg_conv_step): return False
            if t_i % out_t_n_step == 0:
               out_model.write_before_deg(t_i * dt)
            if t_i % proc_t_n_step == 0:
                print("\t\tcalculated: {:.0%}, degraded: {:.2%}".format(t_i/sim_t_n, self.deg_ratio), end="\r")
            t_i += 1
         print()

      # ********** after water inflow ******************
      others_conv_step = self._gen_others_conv_step()
      cont_direct_outflow_step = self._gen_cont_direct_outflow_step()
      set_bent_volume_and_porosity_step = self._gen_set_bent_volume_and_porosity_step()      
      diffusion_and_sorption_step = self._gen_diffusion_and_sorption_step()
      deg_fuel_step = self._gen_deg_fuel_step()
      dissolve_step  = self._gen_dissolve_step()    
      if t_i == T_i_w:
         print("\tAfter water inflow ...")
         print("\t\tTime of water inflow: {:g} years".format(t_i * dt))
         while t_i <= sim_t_n:
            if not next(fuel_conv_step): return False
            if not next(deg_conv_step): return False
            if not next(others_conv_step): return False
            next(cont_direct_outflow_step)
            next(set_bent_volume_and_porosity_step)
            if not next(diffusion_and_sorption_step): return False
            next(deg_fuel_step)      
            next(dissolve_step)
            if t_i % out_t_n_step == 0:
               out_model.write_deg(t_i * dt)
            if t_i % proc_t_n_step == 0:
               print("\t\tcalculated: {:.0%}, degraded: {:.2%}, dissolved: {:.4%}".format(t_i/sim_t_n, self.deg_ratio, self.dissolved_ratio), end="\r")
            t_i += 1
            if self.deg_ratio >= 1: break
         print()

      # ******** after fuel degradation **************
      if t_i <= sim_t_n:
         print("\tAfter total fuel degradation ...")
         while t_i <= sim_t_n:
            if not next(deg_conv_step): return False
            if not next(others_conv_step): return False
            next(cont_direct_outflow_step)
            next(set_bent_volume_and_porosity_step)
            if not next(diffusion_and_sorption_step): return False
            next(dissolve_step)
            if t_i % out_t_n_step == 0:
               out_model.write_after_deg(t_i * dt)
            if t_i % proc_t_n_step == 0:
               print("\t\tcalculated: {:.0%},  dissolved: {:.4%}".format(t_i / sim_t_n, self.dissolved_ratio), end="\r")
            t_i += 1
         print()

      # ********* write statistics **************
      if out_model.statistics is not None: out_model.write_statistics()

      # ********* balance revision **************
      if t_i < T_i_w:
         print("Balance revision:")
         print("\tTotal initial mount in fuel:   {:.12e} mol".format(self.isot_init_fuel_mol.sum()))
         print("\tTotal mount after calculation: {:.12e} mol".format(self.fuel_mol.sum() + self.deg_mol.sum()))
      else:
         print("Balance revision:")
         print("\tTotal initial mount in fuel:   {:.12e} mol".format(self.isot_init_fuel_mol.sum()))
         print("\tTotal mount after calculation: {:.12e} mol".format(self.fuel_mol.sum() + self.deg_mol.sum() + self.w_mol.sum() + self.bent_lay_r_mol.sum() + self.granit_mol.sum()))


      # ********* calculation time **************
      ct = str(datetime.datetime.now() - start_calc_time)
      print("Computing was finished with total time: " + ct + ".")

      return True


