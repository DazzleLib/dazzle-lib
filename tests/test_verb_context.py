"""The capability-side bedrock contract: ``VerbContext`` + the entity-opacity
invariant (context-contract DWP, T2-0/T2-1; AC-T1/AC-T2).

``VerbContext`` names what a consumer's transition context adheres to (apply/undo
over an OPAQUE entity). AC-T1 is the load-bearing invariant: the executor imposes
NO structural type on the transition entity -- a future "just add ``.identity`` to
the entity contract" regression fails loudly here, so the B3c lift can't be undone
silently.
"""
import inspect
from typing import Any

import dazzle_lib.transitions as transitions
from dazzle_lib import TransitionContext, VerbContext


def _ctx():
    # A minimal context -- enough to exist; no transition is ever applied.
    return TransitionContext(
        registry=None, axis_name="x",
        detect=lambda e: None, write=lambda e, t, p: None,
        identity_of=lambda e: "")


def test_transition_context_satisfies_verb_context():   # AC-T2
    # The bedrock executor is its own reference implementation of the contract.
    assert isinstance(_ctx(), VerbContext)


def test_transition_entity_stays_opaque():   # AC-T1 (load-bearing)
    # apply's entity param carries NO structural type (domain-neutral).
    entity_param = inspect.signature(TransitionContext.apply).parameters["entity"]
    assert entity_param.annotation in (Any, inspect.Parameter.empty)
    # the bedrock module imports no consumer entity type -- opacity by design.
    src = inspect.getsource(transitions)
    for forbidden in ("DazzleEntity", "GroupingCapable", "from .entity",
                      "import entity"):
        assert forbidden not in src


def test_verb_context_checks_apply_and_undo_only():
    # runtime_checkable conformance = method presence (apply + undo), nothing more.
    class Conforms:
        def apply(self, entity, target, *, verb): ...
        def undo(self, receipt): ...

    class MissingUndo:
        def apply(self, entity, target, *, verb): ...

    assert isinstance(Conforms(), VerbContext)
    assert not isinstance(MissingUndo(), VerbContext)
