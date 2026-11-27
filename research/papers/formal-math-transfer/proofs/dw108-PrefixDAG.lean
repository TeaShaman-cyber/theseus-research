import Lean
namespace PrefixDAG
variable {V : Type}
inductive Path (r : V → V → Prop) : V → V → Prop where
  | single {a b} : r a b → Path r a b
  | cons {a b c} : r a b → Path r b c → Path r a c
def DAG (r : V → V → Prop) := ∀ v, ¬ Path r v v
theorem path_mono {r s : V → V → Prop}
    (h : ∀ {a b}, r a b → s a b) {a b : V} (p : Path r a b) :
    Path s a b := by
  induction p with
  | single e => exact .single (h e)
  | cons e _ ih => exact .cons (h e) ih
theorem dag_prefix {r s : V → V → Prop}
    (sub : ∀ {a b}, r a b → s a b) (hs : DAG s) : DAG r :=
  fun v p => hs v (path_mono sub p)
theorem all_prefixes_iff_final (graphs : Nat → V → V → Prop) (n : Nat)
    (mono : ∀ k, k ≤ n → ∀ {a b}, graphs k a b → graphs n a b) :
    (∀ k, k ≤ n → DAG (graphs k)) ↔ DAG (graphs n) := by
  constructor
  · intro h; exact h n (Nat.le_refl n)
  · intro h k hk; exact dag_prefix (mono k hk) h
theorem path_rank {r : V → V → Prop} (rank : V → Nat)
    (increasing : ∀ {a b}, r a b → rank a < rank b)
    {a b : V} (p : Path r a b) : rank a < rank b := by
  induction p with
  | single e => exact increasing e
  | cons e _ ih => exact Nat.lt_trans (increasing e) ih
theorem rank_certificate {r : V → V → Prop} (rank : V → Nat)
    (increasing : ∀ {a b}, r a b → rank a < rank b) : DAG r :=
  fun _ p => Nat.lt_irrefl _ (path_rank rank increasing p)
#print axioms path_mono
#print axioms all_prefixes_iff_final
#print axioms rank_certificate
end PrefixDAG
