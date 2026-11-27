import Lean
namespace GraphFilters
variable {V : Type}
inductive Path (r : V → V → Prop) : V → V → Prop where
 | single {a b} : r a b → Path r a b
 | cons {a b c} : r a b → Path r b c → Path r a c
theorem trans {r : V → V → Prop} {a b c : V}
    (p : Path r a b) (q : Path r b c) : Path r a c := by
  induction p with
  | single e => exact .cons e q
  | cons e _ ih => exact .cons e (ih q)
theorem lift {r s : V → V → Prop} (h : ∀ {a b}, r a b → Path s a b)
    {a b : V} (p : Path r a b) : Path s a b := by
  induction p with
  | single e => exact h e
  | cons e _ ih => exact trans (h e) ih
theorem redundant_edge {r : V → V → Prop} {u v : V} (h : Path r u v)
    {a b : V} : Path (fun x y => r x y ∨ (x = u ∧ y = v)) a b ↔ Path r a b := by
  constructor
  · apply lift
    intro x y e
    rcases e with e | ⟨rfl,rfl⟩
    · exact .single e
    · exact h
  · apply lift
    intro x y e
    exact .single (Or.inl e)
theorem component_path {r : V → V → Prop} {C : Type} (label : V → C)
    (h : ∀ {a b}, r a b → label a = label b) {a b : V}
    (p : Path r a b) : label a = label b := by
  induction p with
  | single e => exact h e
  | cons e _ ih => exact (h e).trans ih
theorem rank_path {r : V → V → Prop} (rank : V → Nat)
    (h : ∀ {a b}, r a b → rank a < rank b) {a b : V}
    (p : Path r a b) : rank a < rank b := by
  induction p with
  | single e => exact h e
  | cons e _ ih => exact Nat.lt_trans (h e) ih
theorem rank_restrict {r : V → V → Prop} (rank : V → Nat)
    (h : ∀ {a b}, r a b → rank a < rank b) {a b : V}
    (p : Path r a b) :
    Path (fun x y => r x y ∧ rank y ≤ rank b) a b := by
  induction p with
  | single e => exact .single ⟨e,Nat.le_refl _⟩
  | cons e q ih => exact .cons ⟨e,Nat.le_of_lt (rank_path rank h q)⟩ ih
theorem rank_restrict_iff {r : V → V → Prop} (rank : V → Nat)
    (h : ∀ {a b}, r a b → rank a < rank b) {a b : V} :
    Path (fun x y => r x y ∧ rank y ≤ rank b) a b ↔ Path r a b := by
  constructor
  · apply lift
    intro x y e
    exact .single e.1
  · exact rank_restrict rank h
#print axioms redundant_edge
#print axioms component_path
#print axioms rank_path
#print axioms rank_restrict_iff
end GraphFilters
