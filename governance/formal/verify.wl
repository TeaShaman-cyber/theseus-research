model = Import[FileNameJoin[{DirectoryName[$InputFileName], "project-contract-v12-model.json"}], "RawJSON"];

states = model["states"];
terminals = model["terminals"];
start = model["start"];
success = model["success_terminal"];
required = model["success_requires"];
transitions = model["transitions"];
edges = DirectedEdge[#["from"], #["to"]] & /@ transitions;
graph = Graph[states, edges, DirectedEdges -> True];

nonterminals = Complement[states, terminals];
reachesTerminalQ[v_] := AnyTrue[terminals, GraphDistance[graph, v, #] =!= Infinity &];
allNonterminalsReachTerminal = AllTrue[nonterminals, reachesTerminalQ];
noDeadlockedNonterminals = AllTrue[nonterminals, VertexOutDegree[graph, #] > 0 &];

successRequires = AssociationMap[
  GraphDistance[VertexDelete[graph, #], start, success] === Infinity &,
  required
];

progress = model["fallback_progress"];
returnSpec = progress["return_edge"];
exhaustedSpec = progress["exhausted_edge"];
returnEdge = DirectedEdge[returnSpec["from"], returnSpec["to"]];

fallbackCycleOnly =
  Not[AcyclicGraphQ[graph]] &&
  AcyclicGraphQ[EdgeDelete[graph, returnEdge]];

returnTransitions = Select[
  transitions,
  #["from"] === returnSpec["from"] && #["to"] === returnSpec["to"] &
];
exhaustedTransitions = Select[
  transitions,
  #["from"] === exhaustedSpec["from"] && #["to"] === exhaustedSpec["to"] &
];
fallbackOutgoing = Select[transitions, #["from"] === returnSpec["from"] &];

returnTransitionValid =
  Length[returnTransitions] === 1 &&
  First[returnTransitions]["guard"] === returnSpec["guard"] &&
  First[returnTransitions]["progress_delta"] === progress["return_delta"];

exhaustedTransitionValid =
  Length[exhaustedTransitions] === 1 &&
  First[exhaustedTransitions]["guard"] === exhaustedSpec["guard"] &&
  First[exhaustedTransitions]["progress_delta"] === progress["other_edge_delta"];

fallbackOutgoingExact =
  Length[fallbackOutgoing] === 2 &&
  returnTransitionValid &&
  exhaustedTransitionValid;

otherTransitions = Select[
  transitions,
  Not[#["from"] === returnSpec["from"] && #["to"] === returnSpec["to"]] &
];

otherDeltasValid = AllTrue[
  otherTransitions,
  IntegerQ[#["progress_delta"]] &&
    #["progress_delta"] === progress["other_edge_delta"] &
];

progressMeasureWellFounded =
  progress["measure"] === "remaining_untried_routes" &&
  progress["domain"] === "finite_nonnegative_integer" &&
  IntegerQ[progress["return_delta"]] &&
  progress["return_delta"] < 0 &&
  progress["other_edge_delta"] === 0 &&
  progress["return_enabled_when"] === "positive" &&
  progress["exhausted_enabled_when"] === "zero" &&
  returnTransitionValid &&
  exhaustedTransitionValid &&
  otherDeltasValid;

allowedFallbackGuards = model["allowed_fallback_entry_guards"];
incomingFallback = Select[
  transitions,
  #["to"] === returnSpec["from"] && #["from"] =!= returnSpec["from"] &
];
fallbackGuardsValid = AllTrue[
  incomingFallback,
  MemberQ[allowedFallbackGuards, #["guard"]] &
];

boundedFallback =
  fallbackCycleOnly &&
  fallbackOutgoingExact &&
  progressMeasureWellFounded &&
  fallbackGuardsValid;

receipt = <|
  "Revision" -> model["revision"],
  "AllNonterminalsReachTerminal" -> allNonterminalsReachTerminal,
  "NoDeadlockedNonterminals" -> noDeadlockedNonterminals,
  "SuccessRequires" -> successRequires,
  "FallbackCycleOnly" -> fallbackCycleOnly,
  "FallbackOutgoingExact" -> fallbackOutgoingExact,
  "FallbackProgressMeasure" -> progress["measure"],
  "FallbackReturnDelta" -> progress["return_delta"],
  "ProgressMeasureWellFounded" -> progressMeasureWellFounded,
  "FallbackGuardsValid" -> fallbackGuardsValid,
  "BoundedFallback" -> boundedFallback
|>;

pass = And[
  allNonterminalsReachTerminal,
  noDeadlockedNonterminals,
  And @@ Values[successRequires],
  boundedFallback
];

Print[ExportString[Append[receipt, "Result" -> If[pass, "PASS", "FAIL"]], "RawJSON"]];
If[pass, Exit[0], Exit[1]];
