model = Import[FileNameJoin[{DirectoryName[$InputFileName], "project-contract-v11-model.json"}], "RawJSON"];

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

fallback = model["fallback_return_edge"];
fallbackEdge = DirectedEdge[fallback["from"], fallback["to"]];
fallbackCycleOnly = Not[AcyclicGraphQ[graph]] && AcyclicGraphQ[EdgeDelete[graph, fallbackEdge]];

allowedFallbackGuards = model["allowed_fallback_entry_guards"];
incomingFallback = Select[transitions, #["to"] === fallback["from"] && #["from"] =!= fallback["from"] &];
fallbackGuardsValid = AllTrue[incomingFallback, MemberQ[allowedFallbackGuards, #["guard"]] &];

receipt = <|
  "Revision" -> model["revision"],
  "AllNonterminalsReachTerminal" -> allNonterminalsReachTerminal,
  "NoDeadlockedNonterminals" -> noDeadlockedNonterminals,
  "SuccessRequires" -> successRequires,
  "FallbackCycleOnly" -> fallbackCycleOnly,
  "FallbackGuardsValid" -> fallbackGuardsValid
|>;

pass = And[
  allNonterminalsReachTerminal,
  noDeadlockedNonterminals,
  And @@ Values[successRequires],
  fallbackCycleOnly,
  fallbackGuardsValid
];

Print[ExportString[Append[receipt, "Result" -> If[pass, "PASS", "FAIL"]], "RawJSON"]];
If[pass, Exit[0], Exit[1]];
