import Lean
namespace LedgerDelta
variable {V : Type} (r : V → V → Prop)
def extend (u v x y : V) : Prop := r x y ∨ (r x u ∧ r v y)
theorem extend_refl (refl : ∀ x, r x x) (u v : V) :
    ∀ x, extend r u v x x := fun x => Or.inl (refl x)
theorem extend_trans (tr : ∀ {x y z}, r x y → r y z → r x z) (u v : V) :
    ∀ {x y z}, extend r u v x y → extend r u v y z → extend r u v x z := by
  intro x y z hxy hyz
  rcases hxy with hxy | ⟨hxu,hvy⟩
  · rcases hyz with hyz | ⟨hyu,hvz⟩
    · exact Or.inl (tr hxy hyz)
    · exact Or.inr ⟨tr hxy hyu,hvz⟩
  · rcases hyz with hyz | ⟨hyu,hvz⟩
    · exact Or.inr ⟨hxu,tr hvy hyz⟩
    · exact Or.inr ⟨hxu,hvz⟩
theorem extend_least (s : V → V → Prop)
    (tr : ∀ {x y z}, s x y → s y z → s x z)
    (sub : ∀ {x y}, r x y → s x y) {u v : V} (edge : s u v) :
    ∀ {x y}, extend r u v x y → s x y := by
  intro x y h
  rcases h with h | ⟨hxu,hvy⟩
  · exact sub h
  · exact tr (tr (sub hxu) edge) (sub hvy)
theorem extend_edge (refl : ∀ x, r x x) (u v : V) :
    extend r u v u v := Or.inr ⟨refl u,refl v⟩
theorem extend_antisymm
    (tr : ∀ {x y z}, r x y → r y z → r x z)
    (anti : ∀ {x y}, r x y → r y x → x = y)
    {u v : V} (noReturn : ¬ r v u) :
    ∀ {x y}, extend r u v x y → extend r u v y x → x = y := by
  intro x y hxy hyx
  rcases hxy with hxy | ⟨hxu,hvy⟩
  · rcases hyx with hyx | ⟨hyu,hvx⟩
    · exact anti hxy hyx
    · exact False.elim (noReturn (tr (tr hvx hxy) hyu))
  · rcases hyx with hyx | ⟨hyu,hvx⟩
    · exact False.elim (noReturn (tr (tr hvy hyx) hxu))
    · exact False.elim (noReturn (tr hvy hyu))
theorem extend_antisymm_iff
    (refl : ∀ x, r x x)
    (tr : ∀ {x y z}, r x y → r y z → r x z)
    (anti : ∀ {x y}, r x y → r y x → x = y)
    {u v : V} (distinct : u ≠ v) :
    (∀ {x y}, extend r u v x y → extend r u v y x → x = y) ↔ ¬ r v u := by
  constructor
  · intro h back
    exact distinct (h (extend_edge r refl u v) (Or.inl back))
  · exact extend_antisymm r tr anti
-- General deterministic fixed-observation lower bound for row validity.
theorem no_exact_subset_check {n m : Nat} (q : Fin m → Fin n) (i : Fin n)
    (miss : ∀ j, q j ≠ i) (check : (Fin m → Bool) → Bool)
    (correct : ∀ data : Fin n → Bool, check (fun j => data (q j)) = true ↔
      ∀ k, data k = true) : False := by
  let good : Fin n → Bool := fun _ => true
  let bad : Fin n → Bool := fun k => if k = i then false else true
  have obs : (fun j => good (q j)) = (fun j => bad (q j)) := by
    funext j
    simp [good,bad,miss j]
  have g : check (fun j => good (q j)) = true := (correct good).2 (fun _ => rfl)
  rw [obs] at g
  have impossible := (correct bad).1 g i
  simp [bad] at impossible
#print axioms extend_refl
#print axioms extend_trans
#print axioms extend_least
#print axioms extend_edge
#print axioms extend_antisymm_iff
#print axioms no_exact_subset_check
end LedgerDelta
