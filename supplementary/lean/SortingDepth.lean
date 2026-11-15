import Mathlib.Data.Finset.Sort
import Mathlib.GroupTheory.Perm.Cycle.Basic
import Mathlib.Order.TypeTags

/-!
# A two-layer reduction for sorting-network depth

A layer is an involution on the wires. Fixed points are idle wires, and each
other orbit is one comparator with the minimum sent to the smaller wire.
On wires indexed by `Fin n`, these are ordinary disjoint comparator matchings.

`D_ceil_half_add_two` proves the minimum-depth recurrence. The stronger
`remove_two_layers` constructs a smaller sorter from any sorter with a
two-layer prefix.

Checked with Lean 4.35.0 and Mathlib v4.35.0.
-/

namespace SortingDepth

universe u v

structure Layer (ι : Type u) where
  mate : ι → ι
  inv : Function.Involutive mate

namespace Layer

@[simp] lemma mate_mate {ι : Type*} (L : Layer ι) (i : ι) :
    L.mate (L.mate i) = i := L.inv i

variable {ι : Type u} {κ : Type v}

def perm (L : Layer ι) : Equiv.Perm ι :=
  ⟨L.mate, L.mate, L.mate_mate, L.inv⟩

def relabel (L : Layer ι) (e : κ ≃ ι) : Layer κ :=
  ⟨fun i => e.symm (L.mate (e i)), fun i => by simp [L.mate_mate]⟩

def restrict (L : Layer ι) (p : ι → Prop) [DecidablePred p] : Layer {i // p i} where
  mate i := if h : p (L.mate i.val) then ⟨L.mate i.val, h⟩ else i
  inv i := by
    by_cases h : p (L.mate i.val)
    · simp only [dif_pos h, L.mate_mate, dif_pos i.property]
    · simp [h]

variable [LinearOrder ι] {α : Type*} [LinearOrder α]

def run (L : Layer ι) (x : ι → α) (i : ι) : α :=
  if i ≤ L.mate i then min (x i) (x (L.mate i)) else max (x i) (x (L.mate i))

lemma run_of_fixed (L : Layer ι) (x : ι → α) {i : ι} (h : L.mate i = i) :
    L.run x i = x i := by simp [run, h]

lemma run_of_monotone (L : Layer ι) {x : ι → α} (hx : Monotone x) : L.run x = x := by
  funext i
  by_cases h : i ≤ L.mate i
  · simp [run, h, min_eq_left (hx h)]
  · simp [run, h, max_eq_left (hx (le_of_not_ge h))]

lemma run_mono_of_monotone (L : Layer ι) {β : Type*} [LinearOrder β] {f : α → β}
    (hf : Monotone f) (x : ι → α) : L.run (f ∘ x) = f ∘ L.run x := by
  funext i
  by_cases h : i ≤ L.mate i <;> simp [run, h, hf.map_min, hf.map_max, Function.comp_def]

/-- The switch sends each input wire to the wire holding that value after the layer. -/
def switch (L : Layer ι) (x : ι → α) : Layer ι where
  mate i := if L.run x i = x i then i else L.mate i
  inv i := by
    by_cases h : L.run x i = x i
    · simp [h]
    · have hj : L.run x (L.mate i) ≠ x (L.mate i) := by
        have hi : i ≠ L.mate i := fun e => h (L.run_of_fixed x e.symm)
        rcases lt_or_gt_of_ne hi with hl | hl
        · simp only [run, L.mate_mate, if_pos hl.le] at h
          have hx : x (L.mate i) < x i := lt_of_not_ge (fun hx => h (min_eq_left hx))
          simpa [run, L.mate_mate, not_le_of_gt hl, max_eq_right hx.le] using hx.ne'
        · simp only [run, L.mate_mate, if_neg (not_le_of_gt hl)] at h
          have hx : x i < x (L.mate i) := lt_of_not_ge (fun hx => h (max_eq_left hx))
          simpa [run, L.mate_mate, hl.le, min_eq_right hx.le] using hx.ne
      simp [h, hj, L.inv]

lemma run_switch (L : Layer ι) (x : ι → α) (i : ι) :
    L.run x ((L.switch x).mate i) = x i := by
  by_cases h : L.run x i = x i
  · simp [switch, h]
  · have hi : i ≠ L.mate i := fun e => h (L.run_of_fixed x e.symm)
    have hs : (L.switch x).mate i = L.mate i := by simp [switch, h]
    rw [hs]
    rcases lt_or_gt_of_ne hi with hl | hl
    · have hx : x (L.mate i) ≤ x i := le_of_not_ge (fun hx => h (by simp [run, hl.le, min_eq_left hx]))
      simp [run, L.mate_mate, not_le_of_gt hl, max_eq_right hx]
    · have hx : x i ≤ x (L.mate i) := le_of_not_ge (fun hx => h (by simp [run, not_le_of_gt hl, max_eq_left hx]))
      simp [run, L.mate_mate, hl.le, min_eq_right hx]

lemma run_eq_switch (L : Layer ι) (x : ι → α) (i : ι) :
    L.run x i = x ((L.switch x).mate i) := by
  simpa only [mate_mate] using L.run_switch x ((L.switch x).mate i)

lemma switch_eq_self_iff (L : Layer ι) (x : ι → α) (i : ι) :
    (L.switch x).mate i = i ↔ L.run x i = x i := by
  constructor
  · intro h
    simpa only [h] using L.run_switch x i
  · intro h
    simp [switch, h]

lemma switch_comm (L : Layer ι) (x : ι → α) (i : ι) :
    (L.switch x).mate (L.mate i) = L.mate ((L.switch x).mate i) := by
  by_cases h : L.run x i = x i
  · have hj : (L.switch x).mate (L.mate i) = L.mate i := by
      by_contra hj
      have hh : L.run x (L.mate i) ≠ x (L.mate i) :=
        mt ((L.switch_eq_self_iff x _).mpr) hj
      have hji : (L.switch x).mate (L.mate i) = i := by simp [switch, hh, L.inv]
      have := (L.switch x).inv (L.mate i)
      rw [hji, (L.switch_eq_self_iff x i).mpr h] at this
      exact hj (hji.trans this)
    rw [hj, (L.switch_eq_self_iff x i).mpr h]
  · have hi : (L.switch x).mate i = L.mate i := by simp [switch, h]
    simpa only [hi, mate_mate] using (L.switch x).mate_mate i

end Layer

def run {ι : Type u} {α : Type v} [LinearOrder ι] [LinearOrder α] :
    List (Layer ι) → (ι → α) → ι → α
  | [], x => x
  | L :: N, x => run N (L.run x)

def Sorts {ι : Type u} [LinearOrder ι] (N : List (Layer ι)) : Prop :=
  ∀ x : ι → Bool, Monotone (run N x)

lemma run_append {ι : Type u} {α : Type v} [LinearOrder ι] [LinearOrder α]
    (M N : List (Layer ι)) (x : ι → α) : run (M ++ N) x = run N (run M x) := by
  induction M generalizing x with
  | nil => rfl
  | cons L M ih => exact ih (L.run x)

lemma run_monotone_map {ι : Type u} {α : Type v} {β : Type*} [LinearOrder ι] [LinearOrder α]
    [LinearOrder β] (N : List (Layer ι)) {f : α → β} (hf : Monotone f) (x : ι → α) :
    run N (f ∘ x) = f ∘ run N x := by
  induction N generalizing x with
  | nil => rfl
  | cons L N ih =>
    simp only [run, L.run_mono_of_monotone hf, ih]

/-- The zero-one principle. -/
lemma Sorts.mono_run {ι : Type u} [LinearOrder ι] {N : List (Layer ι)} (h : Sorts N)
    {α : Type v} [LinearOrder α] (x : ι → α) : Monotone (run N x) := by
  intro i j hij
  by_contra hn
  classical
  let f : α → Bool := fun a => decide (run N x i ≤ a)
  have hf : Monotone f := by
    intro a b hab
    by_cases ha : run N x i ≤ a
    · simp [f, ha, ha.trans hab]
    · simp [f, ha]
  have hs := h (f ∘ x) hij
  change run N (f ∘ x) i ≤ run N (f ∘ x) j at hs
  rw [run_monotone_map N hf x] at hs
  have htf : true ≤ false := by simpa [f, Function.comp_apply, hn] using hs
  exact (by decide : ¬ true ≤ false) htf

lemma run_of_monotone {ι : Type u} {α : Type v} [LinearOrder ι] [LinearOrder α]
    (N : List (Layer ι)) {x : ι → α} (hx : Monotone x) : run N x = x := by
  induction N with
  | nil => rfl
  | cons L N ih => simp only [run, L.run_of_monotone hx, ih]

lemma exists_input_perm {ι : Type u} {α : Type v} [LinearOrder ι] [LinearOrder α]
    (N : List (Layer ι)) (x : ι → α) : ∃ e : Equiv.Perm ι, run N x = x ∘ e := by
  induction N generalizing x with
  | nil => exact ⟨Equiv.refl _, rfl⟩
  | cons L N ih =>
    obtain ⟨e, he⟩ := ih (L.run x)
    exact ⟨e.trans (L.switch x).perm,
      funext fun i => (congrFun he i).trans (L.run_eq_switch x (e i))⟩

section Matchings

variable {ι : Type u}

/-- A maximal matching has at most one idle wire. -/
def Layer.Full (L : Layer ι) : Prop := ∀ i j, L.mate i = i → L.mate j = j → i = j

section Fill

variable [LinearOrder ι] [Fintype ι]

private def fixed (L : Layer ι) : Finset ι := Finset.univ.filter fun i => L.mate i = i

private def fillPair (L : Layer ι) (a b : ι) (ha : L.mate a = a) (hb : L.mate b = b)
    (hab : a ≠ b) : Layer ι where
  mate i := if i = a then b else if i = b then a else L.mate i
  inv i := by
    by_cases ia : i = a
    · subst i
      simp [hab, hab.symm]
    by_cases ib : i = b
    · subst i
      simp [hab, hab.symm]
    have hma : L.mate i ≠ a := fun h => ia (L.inv.injective (h.trans ha.symm))
    have hmb : L.mate i ≠ b := fun h => ib (L.inv.injective (h.trans hb.symm))
    simp [ia, ib, hma, hmb]

private def onlyPair (a b : ι) : Layer ι where
  mate := Equiv.swap a b
  inv := Equiv.swap_apply_self a b

omit [Fintype ι] in
private lemma fillPair_run {α : Type*} [LinearOrder α] (L : Layer ι) (a b : ι)
    (ha : L.mate a = a) (hb : L.mate b = b) (hab : a ≠ b) (x : ι → α) :
    (fillPair L a b ha hb hab).run x = L.run ((onlyPair a b).run x) := by
  funext i
  by_cases ia : i = a
  · subst i
    rw [L.run_of_fixed _ ha]
    simp [Layer.run, fillPair, onlyPair]
  by_cases ib : i = b
  · subst i
    rw [L.run_of_fixed _ hb]
    simp [Layer.run, fillPair, onlyPair, hab.symm]
  have hma : L.mate i ≠ a := fun h => ia (L.inv.injective (h.trans ha.symm))
  have hmb : L.mate i ≠ b := fun h => ib (L.inv.injective (h.trans hb.symm))
  have hfix := fun j (ja : j ≠ a) (jb : j ≠ b) =>
    (onlyPair a b).run_of_fixed x (i := j) (Equiv.swap_apply_of_ne_of_ne ja jb)
  have hm : (fillPair L a b ha hb hab).mate i = L.mate i := by simp [fillPair, ia, ib]
  nth_rw 1 [Layer.run]
  nth_rw 1 [Layer.run]
  rw [hm, hfix i ia ib, hfix (L.mate i) hma hmb]

/-- Adding comparators to idle wires in the first layer preserves sorting. -/
lemma exists_full_first (L : Layer ι) (N : List (Layer ι)) (hs : Sorts (L :: N)) :
    ∃ M : Layer ι, M.Full ∧ Sorts (M :: N) := by
  classical
  generalize hk : (fixed L).card = k
  induction k using Nat.strong_induction_on generalizing L with
  | h k ih =>
    by_cases hf : L.Full
    · exact ⟨L, hf, hs⟩
    unfold Layer.Full at hf
    push_neg at hf
    obtain ⟨a, b, ha, hb, hab⟩ := hf
    let M := fillPair L a b ha hb hab
    have hcard : (fixed M).card < (fixed L).card := by
      apply Finset.card_lt_card
      apply Finset.ssubset_iff_subset_ne.mpr
      constructor
      · intro i hi
        have hmi : M.mate i = i := (Finset.mem_filter.mp hi).2
        have ia : i ≠ a := by
          rintro rfl
          exact hab.symm (by simpa [M, fillPair] using hmi)
        have ib : i ≠ b := by
          rintro rfl
          exact hab (by simpa [M, fillPair, hab.symm] using hmi)
        simp [fixed, M, fillPair, ia, ib] at hi
        simpa [fixed] using hi
      · intro he
        have hm : a ∈ fixed M := he ▸ (by simp [fixed, ha] : a ∈ fixed L)
        simp [fixed, M, fillPair, hab.symm] at hm
    refine ih _ (hcard.trans_eq hk) M ?_ rfl
    intro x
    simpa only [run, M, fillPair_run] using hs ((onlyPair a b).run x)

end Fill

/-- Walks use the nontrivial edges of either matching. -/
private inductive Walk (A B : Layer ι) : ι → ι → ℕ → Prop
  | nil (i) : Walk A B i i 0
  | step {i j k : ι} {m : ℕ} (hne : i ≠ j)
      (edge : j = A.mate i ∨ j = B.mate i) (tail : Walk A B j k m) :
      Walk A B i k (m + 1)

private lemma Walk.snoc {A B : Layer ι} {i j k : ι} {m : ℕ} (w : Walk A B i j m)
    (hne : j ≠ k) (he : k = A.mate j ∨ k = B.mate j) : Walk A B i k (m + 1) := by
  induction w with
  | nil => exact Walk.step hne he (Walk.nil k)
  | step hne' he' _ ih => exact Walk.step hne' he' (ih hne he)

private lemma Walk.reverse {A B : Layer ι} {i j : ι} {m : ℕ} (w : Walk A B i j m) :
    Walk A B j i m := by
  induction w with
  | nil => exact Walk.nil _
  | step hne he _ ih =>
    apply ih.snoc hne.symm
    rcases he with h | h
    · exact Or.inl (by rw [h, A.mate_mate])
    · exact Or.inr (by rw [h, B.mate_mate])

private lemma Walk.append {A B : Layer ι} {i j k : ι} {m l : ℕ} (w : Walk A B i j m)
    (w' : Walk A B j k l) : Walk A B i k (m + l) := by
  induction w with
  | nil => simpa using w'
  | step hne he _ ih =>
    rw [Nat.succ_add]
    exact Walk.step hne he (ih w')

private def next (A B : Layer ι) : Bool → ι → ι
  | false => A.mate
  | true => B.mate

private inductive Alt (A B : Layer ι) : Bool → ι → ι → ℕ → Prop
  | nil (b) (i) : Alt A B b i i 0
  | step {b : Bool} {i j : ι} {k : ℕ} (h : next A B b i ≠ i)
      (w : Alt A B (!b) (next A B b i) j k) : Alt A B b i j (k + 1)

private lemma Alt.succ_iff {A B : Layer ι} {b : Bool} {i j : ι} {k : ℕ} :
    Alt A B b i j (k + 1) ↔
      next A B b i ≠ i ∧ Alt A B (!b) (next A B b i) j k := by
  constructor
  · intro w
    cases w with
    | step h w => exact ⟨h, w⟩
  · exact fun ⟨h, w⟩ => Alt.step h w

private lemma Alt.zero_eq {A B : Layer ι} {b : Bool} {i j : ι}
    (w : Alt A B b i j 0) : i = j := by cases w; rfl

private lemma next_next (A B : Layer ι) (b : Bool) (i : ι) :
    next A B b (next A B b i) = i := by cases b <;> simp [next]

/-- An odd alternating closed walk is impossible: remove its first and last edges,
which have the same type, until a loop would be required. -/
private lemma no_alt_odd (A B : Layer ι) (k : ℕ) (b : Bool) (i : ι) :
    ¬ Alt A B b i i (2 * k + 1) := by
  have hlast : ∀ (k : ℕ) (b : Bool) (i j : ι),
      Alt A B b i j (2 * k + 1) → Alt A B b i (next A B b j) (2 * k) := by
    intro k
    induction k with
    | zero =>
      intro b i j w
      have he := (Alt.succ_iff.mp w).2.zero_eq
      rw [← he, next_next]
      exact Alt.nil _ _
    | succ k ih =>
      intro b i j w
      have hlen : 2 * (k + 1) + 1 = (2 * k + 1) + 1 + 1 := by omega
      rw [hlen] at w
      have ⟨h1, w1⟩ := Alt.succ_iff.mp w
      have ⟨h2, w2⟩ := Alt.succ_iff.mp w1
      simp only [Bool.not_not] at w2
      have hw := Alt.step h1 (Alt.step h2 (by simpa only [Bool.not_not] using ih b _ _ w2))
      have he : 2 * (k + 1) = 2 * k + 1 + 1 := by omega
      rw [he]
      exact hw
  induction k generalizing b i with
  | zero =>
    intro w
    have ⟨h, w'⟩ := Alt.succ_iff.mp w
    exact h w'.zero_eq
  | succ k ih =>
    intro w
    have w' := hlast (k + 1) b i i w
    have he : 2 * (k + 1) = (2 * k + 1) + 1 := by omega
    rw [he] at w'
    exact ih (!b) (next A B b i) (Alt.succ_iff.mp w').2

private lemma Alt.toWalk {A B : Layer ι} {b : Bool} {i j : ι} {m : ℕ}
    (w : Alt A B b i j m) : Walk A B i j m := by
  induction w with
  | nil => exact Walk.nil _
  | @step b i j l h hw ih =>
    apply Walk.step h.symm _ ih
    cases b
    · exact Or.inl rfl
    · exact Or.inr rfl

private lemma Walk.alt_or_shorter {A B : Layer ι} {i j : ι} {m : ℕ}
    (w : Walk A B i j m) : (∃ b, Alt A B b i j m) ∨
      (∃ l, Walk A B i j l ∧ l + 2 = m) := by
  induction w with
  | nil => exact Or.inl ⟨false, Alt.nil _ _⟩
  | @step i j k m hne he w ih =>
    rcases ih with ⟨c, hc⟩ | ⟨l, hl, hm⟩
    · obtain ⟨b, hb⟩ : ∃ b, j = next A B b i :=
        he.elim (fun h => ⟨false, h⟩) (fun h => ⟨true, h⟩)
      by_cases e : c = !b
      · subst c j
        exact Or.inl ⟨b, Alt.step hne.symm hc⟩
      · have e' : c = b := by cases b <;> cases c <;> simp_all
        subst c j
        cases hc with
        | nil => exact Or.inl ⟨b, Alt.step hne.symm (Alt.nil _ _)⟩
        | @step _ _ _ l h hc =>
          right
          refine ⟨l, ?_, by omega⟩
          rw [next_next] at hc
          exact hc.toWalk
    · exact Or.inr ⟨l + 1, Walk.step hne he hl, by omega⟩

private lemma Walk.closed_even {A B : Layer ι} {i : ι} {m : ℕ} (w : Walk A B i i m) :
    m % 2 = 0 := by
  induction m using Nat.strong_induction_on with
  | h m ih =>
    rcases w.alt_or_shorter with ⟨b, h⟩ | ⟨l, h, hl⟩
    · by_contra hodd
      have hm : m = 2 * (m / 2) + 1 := by omega
      conv at h => rhs; rw [hm]
      exact no_alt_odd A B (m / 2) b i h
    · have := ih l (by omega) h
      omega

/-- Choose the parity of a walk from a representative of each component. -/
lemma two_colour (A B : Layer ι) (hfull : A.Full) :
    ∃ live : ι → Bool,
      (∀ i, A.mate i ≠ i → live (A.mate i) = !live i) ∧
      (∀ i, B.mate i ≠ i → live (B.mate i) = !live i) ∧
      (∀ i, A.mate i = i → live i = true) := by
  classical
  let reach (i j : ι) := ∃ m, Walk A B i j m
  let s : Setoid ι := ⟨reach, fun i => ⟨0, Walk.nil i⟩,
    fun ⟨m, w⟩ => ⟨m, w.reverse⟩,
    fun ⟨m, w⟩ ⟨l, w'⟩ => ⟨m + l, w.append w'⟩⟩
  let rootOf (q : Quotient s) :=
    if h : ∃ u, A.mate u = u ∧ Quotient.mk s u = q then h.choose else q.out
  let root (i : ι) := rootOf (Quotient.mk s i)
  have hr (i : ι) : reach (root i) i := by
    unfold root rootOf
    split
    · rename_i h
      exact Quotient.exact h.choose_spec.2
    · exact Quotient.exact (Quotient.out_eq (Quotient.mk s i))
  have hroot {i j : ι} (h : reach i j) : root i = root j :=
    congrArg rootOf (Quotient.sound h)
  let len (i : ι) := (hr i).choose
  have hw (i : ι) : Walk A B (root i) i (len i) := (hr i).choose_spec
  let live (i : ι) := decide (len i % 2 = 0)
  have hue {i : ι} (h : A.mate i = i) : root i = i := by
    have he : ∃ u, A.mate u = u ∧ Quotient.mk s u = Quotient.mk s i := ⟨i, h, rfl⟩
    simp only [root, rootOf, dif_pos he]
    exact hfull _ _ he.choose_spec.1 h
  have flip {i j : ι} (hne : i ≠ j) (he : j = A.mate i ∨ j = B.mate i) :
      live j = !live i := by
    have hrj := hw j
    rw [← hroot ⟨1, Walk.step hne he (Walk.nil j)⟩] at hrj
    have w := ((hw i).snoc hne he).append hrj.reverse
    have hp := w.closed_even
    unfold live
    by_cases hi : len i % 2 = 0 <;> by_cases hj : len j % 2 = 0 <;>
      simp only [hi, hj, decide_true, decide_false, Bool.not_true, Bool.not_false] <;> omega
  refine ⟨live, fun i h => flip h.symm (Or.inl rfl), fun i h => flip h.symm (Or.inr rfl), ?_⟩
  intro i hi
  have h := hw i
  rw [hue hi] at h
  simp [live, h.closed_even]

end Matchings

section Pruning

variable {ι : Type u} {κ : Type v} [LinearOrder ι] [LinearOrder κ]

/-- The three possible wire states in the reference run. -/
private abbrev Tag := WithBot (WithTop Unit)
private def mid : Tag := WithBot.some (WithTop.some ())
private def high : Tag := WithBot.some (⊤ : WithTop Unit)
private abbrev Box (α : Type*) := WithBot (WithTop α)
private def value {α : Type*} (a : α) : Box α := WithBot.some (WithTop.some a)
private def encode {α : Type*} (a : α) (t : Tag) : Box α :=
  if t = ⊥ then ⊥ else if t = mid then value a else WithBot.some (⊤ : WithTop α)

private lemma tag_cases (t : Tag) : t = ⊥ ∨ t = mid ∨ t = high := by
  induction t using WithBot.recBotCoe with
  | bot => exact Or.inl rfl
  | coe t =>
    induction t using WithTop.recTopCoe with
    | top => exact Or.inr (Or.inr rfl)
    | coe x => cases x; exact Or.inr (Or.inl rfl)

private lemma mid_ne_bot : mid ≠ ⊥ := by decide
private lemma high_ne_bot : high ≠ ⊥ := by decide
private lemma high_ne_mid : high ≠ mid := by decide

private lemma value_strictMono {α : Type*} [LinearOrder α] :
    StrictMono (value : α → Box α) := fun _ _ => by simp [value, WithBot.coe_lt_coe, WithTop.coe_lt_coe]

private lemma encode_mid {α : Type*} (a : α) : encode a mid = value a := by
  simp [encode, mid_ne_bot]

/-- When two tags differ, the encoded values have the same strict order. -/
private lemma encode_lt {α : Type*} [LinearOrder α] {t s : Tag} (h : t < s) (a b : α) :
    encode a t < encode b s := by
  rcases tag_cases t with rfl | rfl | rfl <;> rcases tag_cases s with rfl | rfl | rfl <;>
    simp [encode, mid_ne_bot, high_ne_bot, high_ne_mid, value, WithBot.coe_lt_coe] at h ⊢ <;>
    first | exact (by decide : ¬ high < mid) h | exact h.elim |
      exact WithBot.bot_lt_coe _ | exact WithBot.coe_lt_coe.mpr (WithTop.coe_lt_top a)

private lemma encode_same {α : Type*} (a b : α) {t : Tag} (h : t ≠ mid) :
    encode a t = encode b t := by simp [encode, h]

/-- `p` labels the live wires. Its order may change during pruning. -/
private abbrev Labels (t : ι → Tag) (κ : Type*) := κ ≃ {i : ι // t i = mid}

private def embed {t : ι → Tag} (p : Labels t κ) (i : κ) : ι := (p i).val

omit [LinearOrder ι] [LinearOrder κ] in
private lemma embed_injective {t : ι → Tag} (p : Labels t κ) : Function.Injective (embed p) :=
  fun _ _ h => p.injective (Subtype.ext h)

private def pack {α : Type*} {t : ι → Tag} (p : Labels t κ) (x : κ → α) (fallback : α)
    (i : ι) : Box α :=
  if h : t i = mid then value (x (p.symm ⟨i, h⟩)) else encode fallback (t i)

omit [LinearOrder ι] [LinearOrder κ] in
private lemma pack_live {α : Type*} {t : ι → Tag} (p : Labels t κ) (x : κ → α)
    (z : α) (i : κ) : pack p x z (embed p i) = value (x i) := by
  simp [pack, embed, (p i).property]

omit [LinearOrder ι] [LinearOrder κ] in
private lemma pack_encode {α : Type*} {t : ι → Tag} (p : Labels t κ) (x : κ → α)
    (z : α) (i : ι) : ∃ a : α, pack p x z i = encode a (t i) := by
  by_cases h : t i = mid
  · exact ⟨x (p.symm ⟨i, h⟩), by simp [pack, h, encode_mid]⟩
  · exact ⟨z, by simp [pack, h]⟩

private def cut (L : Layer ι) {t : ι → Tag} (p : Labels t κ) : Layer κ :=
  (L.restrict fun i => t i = mid).relabel p

omit [LinearOrder ι] [LinearOrder κ] in
private lemma cut_mate_of_live (L : Layer ι) {t : ι → Tag} (p : Labels t κ) (i : κ)
    (h : t (L.mate (embed p i)) = mid) :
    embed p ((cut L p).mate i) = L.mate (embed p i) := by
  simp [cut, Layer.restrict, Layer.relabel, embed] at h ⊢
  simp [h]

omit [LinearOrder ι] [LinearOrder κ] in
private lemma cut_mate_of_dead (L : Layer ι) {t : ι → Tag} (p : Labels t κ) (i : κ)
    (h : t (L.mate (embed p i)) ≠ mid) : (cut L p).mate i = i := by
  simp [cut, Layer.restrict, Layer.relabel, embed] at h ⊢
  simp [h]

private def tagLabels (L : Layer ι) (t : ι → Tag) :
    {i : ι // t i = mid} ≃ {i : ι // L.run t i = mid} where
  toFun i := ⟨(L.switch t).mate i, (L.run_switch t i).trans i.property⟩
  invFun i := ⟨(L.switch t).mate i, (L.run_eq_switch t i).symm.trans i.property⟩
  left_inv i := Subtype.ext ((L.switch t).mate_mate i.val)
  right_inv i := Subtype.ext ((L.switch t).mate_mate i.val)

/-- Update the labels after a reference run, then reverse the labels of each
live-live comparator whose orientation disagrees with the reduced wire order. -/
private def advance (L : Layer ι) {t : ι → Tag} (p : Labels t κ) : Labels (L.run t) κ :=
  ((cut L p).switch (embed p)).perm.trans (p.trans (tagLabels L t))

private lemma advance_embed (L : Layer ι) {t : ι → Tag} (p : Labels t κ) (i : κ) :
    embed (advance L p) i =
      (L.switch t).mate (embed p (((cut L p).switch (embed p)).mate i)) := rfl

private lemma run_encoded_of_not_both_live {α : Type*} [LinearOrder α]
    (L : Layer ι) (t : ι → Tag) (y : ι → Box α) (i : ι) (a b : α)
    (ha : y i = encode a (t i)) (hb : y (L.mate i) = encode b (t (L.mate i)))
    (hn : ¬ (t i = mid ∧ t (L.mate i) = mid)) :
    L.run y i = y ((L.switch t).mate i) := by
  rcases lt_trichotomy (t i) (t (L.mate i)) with ht | ht | ht
  · have hy : y i < y (L.mate i) := by rw [ha, hb]; exact encode_lt ht a b
    by_cases h : i ≤ L.mate i
    · have he : L.run t i = t i := by simp [Layer.run, h, min_eq_left ht.le]
      rw [(L.switch_eq_self_iff t i).mpr he]
      simp [Layer.run, h, min_eq_left hy.le]
    · have he : L.run t i ≠ t i := by simp [Layer.run, h, max_eq_right ht.le, ht.ne']
      have hsw : (L.switch t).mate i = L.mate i := by simp [Layer.switch, he]
      rw [hsw]
      simp [Layer.run, h, max_eq_right hy.le]
  · have htm : t (L.mate i) ≠ mid := fun h => hn ⟨ht.trans h, h⟩
    have hy : y i = y (L.mate i) := by
      rw [ha, hb, ht, encode_same a b htm]
    have he : L.run t i = t i := by simp [Layer.run, ← ht]
    rw [(L.switch_eq_self_iff t i).mpr he]
    simp [Layer.run, ← hy]
  · have hy : y (L.mate i) < y i := by rw [ha, hb]; exact encode_lt ht b a
    by_cases h : i ≤ L.mate i
    · have he : L.run t i ≠ t i := by simp [Layer.run, h, min_eq_right ht.le, ht.ne]
      have hsw : (L.switch t).mate i = L.mate i := by simp [Layer.switch, he]
      rw [hsw]
      simp [Layer.run, h, min_eq_right hy.le]
    · have he : L.run t i = t i := by simp [Layer.run, h, max_eq_left ht.le]
      rw [(L.switch_eq_self_iff t i).mpr he]
      simp [Layer.run, h, max_eq_left hy.le]

private lemma Layer.run_pack {α : Type*} [LinearOrder α] (L : Layer ι) {t : ι → Tag}
    (p : Labels t κ) (x : κ → α) (z : α) :
    L.run (pack p x z) = pack (advance L p) ((cut L p).run x) z := by
  funext k
  by_cases hk : L.run t k = mid
  · obtain ⟨i, hi⟩ := (advance L p).surjective ⟨k, hk⟩
    have he : embed (advance L p) i = k := congrArg Subtype.val hi
    rw [← he, pack_live, advance_embed]
    let j := (cut L p).mate i
    let a := embed p i
    let b := L.mate a
    by_cases hb : t b = mid
    · have hbj : b = embed p j := (cut_mate_of_live L p i hb).symm
      have ha : t a = mid := (p i).property
      have hpa : pack p x z a = value (x i) := pack_live p x z i
      have hpb : pack p x z b = value (x j) := by rw [hbj, pack_live]
      have hsa : (L.switch t).mate a = a := by
        apply (L.switch_eq_self_iff t a).mpr
        change t (L.mate a) = mid at hb
        simp [Layer.run, ha, hb]
      have hsb : (L.switch t).mate b = b := by
        change (L.switch t).mate (L.mate a) = L.mate a
        rw [L.switch_comm, hsa]
      change L.run (pack p x z)
        ((L.switch t).mate (embed p (((cut L p).switch (embed p)).mate i))) = _
      have hba : L.mate b = a := L.mate_mate a
      have hj' : (cut L p).mate i = j := rfl
      have hcut : (cut L p).run (embed p) i = if i ≤ j then min a b else max a b := by
        simp only [Layer.run, hj', ← hbj, a]
      have hswitch : ((cut L p).switch (embed p)).mate i =
          if (if i ≤ j then min a b else max a b) = a then i else j := by
        change (if (cut L p).run (embed p) i = a then i else (cut L p).mate i) = _
        rw [hcut, hj']
      have hL₁ : L.run (pack p x z) a =
          if a ≤ b then min (value (x i)) (value (x j)) else max (value (x i)) (value (x j)) := by
        unfold Layer.run
        change (if a ≤ b then min _ _ else max _ _) = _
        rw [hpa, hpb]
      have hL₂ : L.run (pack p x z) b =
          if b ≤ a then min (value (x j)) (value (x i)) else max (value (x j)) (value (x i)) := by
        simp only [Layer.run, hba, hpa, hpb]
      rw [hswitch]
      have hmin : value (min (x i) (x j)) = min (value (x i)) (value (x j)) :=
        (value_strictMono (α := α)).monotone.map_min
      have hmax : value (max (x i) (x j)) = max (value (x i)) (value (x j)) :=
        (value_strictMono (α := α)).monotone.map_max
      have haj : embed p j = b := hbj.symm
      by_cases hij : i ≤ j
      · by_cases hab : a ≤ b
        · rw [if_pos hij, min_eq_left hab, if_pos rfl]
          change L.run (pack p x z) ((L.switch t).mate a) = _
          rw [hsa, hL₁, if_pos hab]
          simpa only [Layer.run, hj', if_pos hij] using hmin.symm
        · have hba' : b < a := lt_of_not_ge hab
          rw [if_pos hij, min_eq_right hba'.le, if_neg hba'.ne, haj, hsb, hL₂, if_pos hba'.le, min_comm]
          simpa only [Layer.run, hj', if_pos hij] using hmin.symm
      · by_cases hab : a < b
        · rw [if_neg hij, max_eq_right hab.le, if_neg hab.ne', haj, hsb, hL₂,
            if_neg (not_le_of_gt hab), max_comm]
          simpa only [Layer.run, hj', if_neg hij] using hmax.symm
        · have hba' : b ≤ a := le_of_not_gt hab
          have hne : a ≠ b := fun hh => hij (le_of_eq (embed_injective p (hh.trans hbj)))
          have hab' : ¬ a ≤ b := fun hh => hne (le_antisymm hh hba')
          rw [if_neg hij, max_eq_left hba', if_pos rfl]
          change L.run (pack p x z) ((L.switch t).mate a) = _
          rw [hsa, hL₁, if_neg hab']
          simpa only [Layer.run, hj', if_neg hij] using hmax.symm
    · have hj : (cut L p).mate i = i := cut_mate_of_dead L p i hb
      have hc : ((cut L p).switch (embed p)).mate i = i :=
        ((cut L p).switch_eq_self_iff _ _).mpr ((cut L p).run_of_fixed _ hj)
      rw [hc, (cut L p).run_of_fixed x hj]
      change L.run (pack p x z) ((L.switch t).mate a) = value (x i)
      let k' := (L.switch t).mate a
      obtain ⟨c, hc'⟩ := pack_encode p x z k'
      obtain ⟨d, hd'⟩ := pack_encode p x z (L.mate k')
      have hn : ¬ (t k' = mid ∧ t (L.mate k') = mid) := by
        intro h
        change t (L.mate a) ≠ mid at hb
        rcases (show k' = a ∨ k' = L.mate a from by
          change (if L.run t a = t a then a else L.mate a) = a ∨ _
          split <;> simp [k', Layer.switch, *]) with hh | hh
        · exact hb (by simpa [hh] using h.2)
        · exact hb (by simpa [hh] using h.1)
      rw [run_encoded_of_not_both_live L t _ k' c d hc' hd' hn]
      change pack p x z ((L.switch t).mate ((L.switch t).mate a)) = _
      rw [Layer.mate_mate, pack_live]
  · obtain ⟨a, ha⟩ := pack_encode p x z k
    obtain ⟨b, hb⟩ := pack_encode p x z (L.mate k)
    have hn : ¬ (t k = mid ∧ t (L.mate k) = mid) := by
      rintro ⟨h₁, h₂⟩
      exact hk (by simp [Layer.run, h₁, h₂])
    rw [run_encoded_of_not_both_live L t _ k a b ha hb hn]
    have ht := L.run_eq_switch t k
    simp [pack, hk, ← ht]

private def finalLabels (N : List (Layer ι)) (t : ι → Tag) :
    Labels t κ → Labels (run N t) κ :=
  match N with
  | [] => id
  | L :: N => fun p => finalLabels N (L.run t) (advance L p)

private def reduced (N : List (Layer ι)) (t : ι → Tag) : Labels t κ → List (Layer κ) :=
  match N with
  | [] => fun _ => []
  | L :: N => fun p => cut L p :: reduced N (L.run t) (advance L p)

private lemma reduced_length (N : List (Layer ι)) (t : ι → Tag) (p : Labels t κ) :
    (reduced N t p).length = N.length := by
  induction N generalizing t with
  | nil => rfl
  | cons L N ih => simp [reduced, ih]

private lemma run_pack {α : Type*} [LinearOrder α] (N : List (Layer ι)) (t : ι → Tag)
    (p : Labels t κ) (x : κ → α) (z : α) :
    run N (pack p x z) = pack (finalLabels N t p) (run (reduced N t p) x) z := by
  induction N generalizing t x with
  | nil => rfl
  | cons L N ih => simp only [run, reduced, finalLabels, L.run_pack, ih]

private lemma reduced_sorts {N : List (Layer ι)} (hs : Sorts N) (t : ι → Tag) (p : Labels t κ) :
    Sorts (reduced N t p) := by
  have hfinal : StrictMono (embed (finalLabels N t p)) := by
    intro i j hij
    by_contra hn
    have hle := le_of_not_gt hn
    have hm := (hs.mono_run (pack p (id : κ → κ) i)) hle
    rw [run_pack N t p, pack_live, pack_live, run_of_monotone _ monotone_id] at hm
    exact (not_le_of_gt hij) (value_strictMono.le_iff_le.mp hm)
  intro x i j hij
  have hm := (hs.mono_run (pack p x false)) (hfinal.monotone hij)
  rw [run_pack N t p, pack_live, pack_live] at hm
  exact value_strictMono.le_iff_le.mp hm

omit [LinearOrder ι] in
private lemma cut_run_eq_self (L : Layer ι) {t : ι → Tag} (p : Labels t κ)
    (h : ∀ i, t i = mid → t (L.mate i) = mid → L.mate i = i)
    {α : Type*} [LinearOrder α] (x : κ → α) : (cut L p).run x = x := by
  funext i
  apply (cut L p).run_of_fixed
  by_cases hi : t (L.mate (embed p i)) = mid
  · apply embed_injective p
    rw [cut_mate_of_live L p i hi]
    exact h _ (p i).property hi
  · exact cut_mate_of_dead L p i hi

private def mask (A : Layer ι) (live : ι → Bool) (i : ι) : Tag :=
  if live i then mid else if i ≤ A.mate i then ⊥ else high

private lemma mask_is_mid (A : Layer ι) (live : ι → Bool) (i : ι) :
    mask A live i = mid ↔ live i = true := by
  by_cases h : live i = true <;> by_cases hh : i ≤ A.mate i <;>
    simp [mask, h, hh, mid_ne_bot.symm, high_ne_mid]

private lemma mask_fixed (A : Layer ι) (live : ι → Bool)
    (h : ∀ i, A.mate i ≠ i → live (A.mate i) = !live i) : A.run (mask A live) = mask A live := by
  funext i
  by_cases he : A.mate i = i
  · exact A.run_of_fixed _ he
  have hm := h i he
  rcases lt_or_gt_of_ne (Ne.symm he) with hlt | hlt <;> cases hi : live i <;>
    simp [hi] at hm <;>
    simp [Layer.run, mask, hi, hm, hlt.le, not_le_of_gt hlt, high, mid,
      WithBot.coe_le_coe.mpr (le_top : (WithTop.some () : WithTop Unit) ≤ ⊤)]

private lemma mask_no_comparator (A L : Layer ι) (live : ι → Bool)
    (h : ∀ i, L.mate i ≠ i → live (L.mate i) = !live i) :
    ∀ i, mask A live i = mid → mask A live (L.mate i) = mid → L.mate i = i := by
  intro i hi hj
  by_contra he
  have hf := h i he
  rw [(mask_is_mid A live i).mp hi, (mask_is_mid A live _).mp hj] at hf
  exact (by decide : true ≠ !true) hf

private lemma card_live {n : ℕ} (A : Layer (Fin n)) (live : Fin n → Bool) (hfull : A.Full)
    (h : ∀ i, A.mate i ≠ i → live (A.mate i) = !live i)
    (hi : ∀ i, A.mate i = i → live i = true) :
    (Finset.univ.filter fun i => live i = true).card = (n + 1) / 2 := by
  classical
  let good := Finset.univ.filter fun i => live i = true
  let bad := Finset.univ.filter fun i => live i ≠ true
  let idle := Finset.univ.filter fun i => A.mate i = i
  have gid : (bad.image A.mate) ∪ idle = good := by
    ext i
    simp only [Finset.mem_union, Finset.mem_image, good, bad, idle, Finset.mem_filter,
      Finset.mem_univ, true_and]
    constructor
    · rintro (⟨j, hj, rfl⟩ | hj)
      · have hm : A.mate j ≠ j := fun he => hj (hi j he)
        rw [h j hm]
        cases hj' : live j <;> simp_all
      · exact hi i hj
    · intro hg
      by_cases he : A.mate i = i
      · exact Or.inr he
      · exact Or.inl ⟨A.mate i, by simp [h i he, hg], A.mate_mate i⟩
  have hdis : Disjoint (bad.image A.mate) idle := by
    apply Finset.disjoint_left.mpr
    intro i hi' hfix
    obtain ⟨j, hj, rfl⟩ := Finset.mem_image.mp hi'
    have hj' : live j ≠ true := (Finset.mem_filter.mp hj).2
    have hfix' : A.mate (A.mate j) = A.mate j := (Finset.mem_filter.mp hfix).2
    exact hj' (hi j ((A.mate_mate j).symm.trans hfix').symm)
  have hc : good.card = bad.card + idle.card := by
    rw [← gid, Finset.card_union_of_disjoint hdis,
      Finset.card_image_of_injective _ A.inv.injective]
  have hs : good.card + bad.card = n := by
    simpa only [good, bad, Finset.card_univ, Fintype.card_fin] using
      (Finset.card_filter_add_card_filter_not (s := Finset.univ) fun i => live i = true)
  have hidle : idle.card ≤ 1 := by
    apply Finset.card_le_one.mpr
    intro i hi' j hj
    exact hfull i j (Finset.mem_filter.mp hi').2 (Finset.mem_filter.mp hj).2
  change good.card = _
  omega

/-- Any sorter with two initial layers yields a sorter on the ceiling of half
as many wires, with exactly those two layers removed from its depth. -/
theorem remove_two_layers {n : ℕ} (A B : Layer (Fin n)) (N : List (Layer (Fin n)))
    (hs : Sorts (A :: B :: N)) :
    ∃ M : List (Layer (Fin ((n + 1) / 2))), Sorts M ∧ M.length = N.length := by
  obtain ⟨A, hfull, hs⟩ := exists_full_first A (B :: N) hs
  obtain ⟨live, hA, hB, hi⟩ := two_colour A B hfull
  let t := mask A live
  have ht : A.run t = t := mask_fixed A live hA
  let s := Finset.univ.filter fun i => live i = true
  have hsc : s.card = (n + 1) / 2 := card_live A live hfull hA hi
  let e : {i : Fin n // i ∈ s} ≃ {i : Fin n // t i = mid} := by
    apply Equiv.subtypeEquivRight
    intro i
    simp [s, t, mask_is_mid]
  let p : Labels t (Fin ((n + 1) / 2)) := (s.orderIsoOfFin hsc).toEquiv.trans e
  let p₁ := advance A p
  let p₂ := advance B p₁
  refine ⟨reduced N (B.run (A.run t)) p₂, ?_, reduced_length _ _ _⟩
  have hs' := reduced_sorts hs t p
  intro x
  have h1 : (cut A p).run x = x := cut_run_eq_self A p (mask_no_comparator A A live hA) x
  have hb : ∀ i, A.run t i = mid → A.run t (B.mate i) = mid → B.mate i = i := by
    rw [ht]
    exact mask_no_comparator A B live hB
  have h2 : (cut B p₁).run x = x := cut_run_eq_self B p₁ hb x
  simpa only [reduced, run, h1, h2, p₁, p₂] using hs' x

end Pruning
section Depth

private def onlyOne {n : ℕ} (a : Fin n) : Fin n → Bool := fun i => decide (i = a)

private lemma mono_onlyOne {n : ℕ} {a b : Fin n} (h : Monotone (onlyOne a)) (hab : a ≤ b) :
    a = b := by
  by_contra hne
  have hh : true ≤ false := by simpa [onlyOne, Ne.symm hne] using h hab
  exact (by decide : ¬ true ≤ false) hh

private lemma run_onlyOne {n : ℕ} (L : Layer (Fin n)) (a : Fin n) :
    L.run (onlyOne a) = onlyOne ((L.switch (onlyOne a)).mate a) := by
  funext i
  rw [L.run_eq_switch]
  simp only [onlyOne]
  have hin := (L.switch (onlyOne a)).inv
  congr 1
  exact propext ⟨fun h => ((hin i).symm.trans (congrArg _ h)),
    fun h => (congrArg (L.switch (onlyOne a)).mate h).trans (hin a)⟩

/-- On at least three wires a sorter has at least two layers. -/
lemma two_le_length {n : ℕ} (hn : 3 ≤ n) {N : List (Layer (Fin n))} (hs : Sorts N) :
    2 ≤ N.length := by
  let a : Fin n := ⟨0, by omega⟩
  let b : Fin n := ⟨1, by omega⟩
  let c : Fin n := ⟨n - 1, by omega⟩
  have ha : a ≠ b := by intro h; have := congrArg Fin.val h; simp [a, b] at this
  have hc (i : Fin n) : i ≤ c := by change i.val ≤ n - 1; omega
  cases N with
  | nil =>
    have hmono : Monotone (onlyOne a) := hs _
    have e : a = c := mono_onlyOne hmono (hc a)
    have e' : a.val = n - 1 := congrArg Fin.val e
    simp [a] at e'
    omega
  | cons L N =>
    cases N with
    | nil =>
      have hit (i : Fin n) : i = c ∨ L.mate i = c := by
        have h : Monotone (L.run (onlyOne i)) := hs _
        rw [run_onlyOne] at h
        have he := mono_onlyOne h (hc _)
        change (if L.run (onlyOne i) i = onlyOne i i then i else L.mate i) = c at he
        split at he <;> aesop
      have e1 : L.mate a = c := (hit a).resolve_left (by
        intro h; have he : a.val = n - 1 := congrArg Fin.val h
        simp [a] at he; omega)
      have e2 : L.mate b = c := (hit b).resolve_left (by
        intro h; have he : b.val = n - 1 := congrArg Fin.val h
        simp [b] at he; omega)
      exact (ha (L.inv.injective (e1.trans e2.symm))).elim
    | cons L' N => simp

private def castLower (L : Layer (Fin n)) : Layer (Fin (n + 1)) where
  mate := Fin.lastCases (Fin.last n) (fun i => (L.mate i).castSucc)
  inv i := by
    refine Fin.lastCases ?_ (fun j => ?_) i <;> simp

private lemma castLower_run (L : Layer (Fin n)) (x : Fin (n + 1) → Bool) :
    (fun i => (castLower L).run x i.castSucc) = L.run (fun i => x i.castSucc) := by
  funext i
  simp [Layer.run, castLower, Fin.castSucc_le_castSucc_iff]

private lemma run_castLower (N : List (Layer (Fin n))) (x : Fin (n + 1) → Bool) :
    (fun i => run (N.map castLower) x i.castSucc) = run N (fun i => x i.castSucc) := by
  induction N generalizing x with
  | nil => rfl
  | cons L N ih =>
    simp only [List.map_cons, run, ih, castLower_run]

private lemma run_castLower_last (N : List (Layer (Fin n))) (x : Fin (n + 1) → Bool) :
    run (N.map castLower) x (Fin.last n) = x (Fin.last n) := by
  induction N generalizing x with
  | nil => rfl
  | cons L N ih =>
    simp only [List.map_cons, run, ih]
    exact (castLower L).run_of_fixed _ (by simp [castLower])

/-- Compare every lower wire to the last wire, placing the maximum on the last wire. -/
private def maxPrefix (n : ℕ) : List (Layer (Fin (n + 1))) :=
  (List.finRange n).map fun i => onlyPair i.castSucc (Fin.last n)

private lemma maxPrefix_last (n : ℕ) (x : Fin (n + 1) → Bool) (i : Fin (n + 1)) :
    x i ≤ run (maxPrefix n) x (Fin.last n) := by
  let layer := fun (i : Fin n) => onlyPair i.castSucc (Fin.last n)
  have hlast (i : Fin n) (y : Fin (n + 1) → Bool) :
      (layer i).run y (Fin.last n) = max (y (Fin.last n)) (y i.castSucc) := by
    simp [Layer.run, layer, onlyPair, not_le_of_gt (Fin.castSucc_lt_last i)]
  have hfix (i j : Fin n) (hij : i ≠ j) (y : Fin (n + 1) → Bool) :
      (layer i).run y j.castSucc = y j.castSucc := by
    apply Layer.run_of_fixed
    have hne : j.castSucc ≠ i.castSucc := fun h => hij (Fin.castSucc_injective _ h).symm
    have hlast : j.castSucc ≠ Fin.last n := (Fin.castSucc_lt_last j).ne
    simp [layer, onlyPair, Equiv.swap_apply_def, hne, hlast]
  have helper (l : List (Fin n)) (y : Fin (n + 1) → Bool) :
      y (Fin.last n) ≤ run (l.map layer) y (Fin.last n) ∧
      (∀ j ∈ l, y j.castSucc ≤ run (l.map layer) y (Fin.last n)) := by
    induction l generalizing y with
    | nil => simp [run]
    | cons a l ih =>
      have h := ih ((layer a).run y)
      have hb := h.1
      rw [hlast] at hb
      constructor
      · exact (le_max_left _ _).trans hb
      · intro j hj
        by_cases e : j = a
        · subst j
          exact (le_max_right _ _).trans hb
        · have hj' : j ∈ l := (List.mem_cons.mp hj).resolve_left e
          have hh := h.2 j hj'
          rw [hfix a j (Ne.symm e)] at hh
          exact hh
  refine Fin.lastCases ((helper (List.finRange n) x).1) (fun j => ?_) i
  exact (helper (List.finRange n) x).2 j (List.mem_finRange j)

/-- Sorters exist: move a maximum to the last wire, then sort the lower wires. -/
lemma sorter_exists (n : ℕ) : ∃ N : List (Layer (Fin n)), Sorts N := by
  induction n with
  | zero => exact ⟨[], fun _ i => Fin.elim0 i⟩
  | succ n ih =>
    obtain ⟨N, hN⟩ := ih
    refine ⟨maxPrefix n ++ N.map castLower, ?_⟩
    intro x i j hij
    rw [run_append]
    let y := run (maxPrefix n) x
    change run (N.map castLower) y i ≤ run (N.map castLower) y j
    have hlast := run_castLower_last N y
    have hlower := run_castLower N y
    have hmax (i : Fin (n + 1)) : y i ≤ y (Fin.last n) := by
      obtain ⟨e, he⟩ := exists_input_perm (maxPrefix n) x
      calc
        y i = x (e i) := congrFun he i
        _ ≤ y (Fin.last n) := maxPrefix_last n x (e i)
    refine Fin.lastCases ?_ (fun j' => ?_) j hij
    · intro _
      rw [hlast]
      obtain ⟨e, he⟩ := exists_input_perm (N.map castLower) y
      rw [he]
      exact hmax (e i)
    · intro hij'
      revert hij'
      refine Fin.lastCases ?_ (fun i' hi' => ?_) i
      · intro h
        exact ((not_le_of_gt (Fin.castSucc_lt_last j')) h).elim
      · have hm := hN (fun k => y k.castSucc) (Fin.castSucc_le_castSucc_iff.mp hi')
        rwa [← congrFun hlower i', ← congrFun hlower j'] at hm

private def HasDepth (n d : ℕ) : Prop :=
  ∃ N : List (Layer (Fin n)), Sorts N ∧ N.length = d

private lemma exists_depth (n : ℕ) : ∃ d, HasDepth n d := by
  obtain ⟨N, h⟩ := sorter_exists n
  exact ⟨N.length, N, h, rfl⟩

/-- The least depth among standard sorting networks on `n` wires. -/
noncomputable def D (n : ℕ) : ℕ := by
  classical
  exact Nat.find (exists_depth n)

lemma D_le_length {n : ℕ} {N : List (Layer (Fin n))} (h : Sorts N) : D n ≤ N.length := by
  classical
  exact Nat.find_min' (exists_depth n) ⟨N, h, rfl⟩

/-- The two-layer lower-bound recurrence for sorting-network depth. -/
theorem D_ceil_half_add_two (n : ℕ) (hn : 3 ≤ n) : D ((n + 1) / 2) + 2 ≤ D n := by
  classical
  obtain ⟨N, hs, hd⟩ := Nat.find_spec (exists_depth n)
  change N.length = D n at hd
  have hlen := two_le_length hn hs
  rcases N with _ | ⟨A, _ | ⟨B, N⟩⟩
  · simp at hlen
  · simp at hlen
  obtain ⟨M, hm, hmlen⟩ := remove_two_layers A B N hs
  have h := D_le_length hm
  rw [hmlen] at h
  simp only [List.length_cons] at hd
  omega

end Depth
end SortingDepth

#print axioms SortingDepth.remove_two_layers
#print axioms SortingDepth.D_ceil_half_add_two
