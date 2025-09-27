// --------------------------------------------------
// CLEAN START
// --------------------------------------------------
MATCH (n) DETACH DELETE n;

// --------------------------------------------------
// CORE PROJECT NODE
// --------------------------------------------------
MERGE (p:Project {id:"P1"}) SET p.name = "Sample Project";

// --------------------------------------------------
// BUDGET & LINE ITEM
// --------------------------------------------------
MATCH (p:Project {id:"P1"})
MERGE (b:Budget {id:"B1"}) SET b.total = 100000
MERGE (li:Line_Item {id:"LI1"}) SET li.description="Hosting", li.budget=40000
MERGE (b)-[:HAS_LINE_ITEM]->(li)
MERGE (p)-[:HAS_BUDGET]->(b);

// --------------------------------------------------
// STAKEHOLDER, CLIENT, ROLE
// --------------------------------------------------
MATCH (p:Project {id:"P1"})
MERGE (s:Stakeholder {id:"S1"}) SET s.name = "John Brown"
MERGE (c:Client {id:"C1"}) SET c.name="Client A"
MERGE (r:Role {id:"R1"}) SET r.name="Sponsor"
MERGE (s)-[:PLAYS_ROLE]->(r)
MERGE (c)-[:OWNED_BY]->(s)
MERGE (p)-[:HAS_STAKEHOLDER]->(s)
MERGE (p)-[:HAS_CLIENT]->(c);

// --------------------------------------------------
// FEATURE
// --------------------------------------------------
MATCH (p:Project {id:"P1"})
MERGE (f:Feature {id:"F1"}) SET f.name = "User Authentication"
MERGE (p)-[:DELIVERS]->(f);

// --------------------------------------------------
// RISK
// --------------------------------------------------
MATCH (p:Project {id:"P1"}), (f:Feature {id:"F1"})
MERGE (r:Risk {id:"R1"})
  ON CREATE SET r.description="Security Breach", r.probability="High", r.cost=50000
MERGE (p)-[:FACES]->(r)
MERGE (r)-[:THREATENS]->(f);

// --------------------------------------------------
// REQUIREMENT + FUNCTIONAL REQUIREMENT
// --------------------------------------------------
MATCH (p:Project {id:"P1"}), (s:Stakeholder {id:"S1"}), (f:Feature {id:"F1"})
MERGE (req:Requirement {id:"REQ1"})
  ON CREATE SET req.type="Functional", req.description="Users must log in"
MERGE (req)-[:RAISED_BY]->(s)
MERGE (req)-[:SATISFIED_BY]->(f)
MERGE (p)-[:HAS_REQUIREMENT]->(req);

MATCH (p:Project {id:"P1"}), (req:Requirement {id:"REQ1"})
MERGE (fr:Functional_Requirement {id:"FR1"})
  ON CREATE SET fr.description="OAuth2 authentication flow"
MERGE (req)-[:HAS_FUNCTIONAL]->(fr);

// --------------------------------------------------
// CONSTRAINTS + QUALITY SCENARIOS
// --------------------------------------------------
MATCH (p:Project {id:"P1"}), (f:Feature {id:"F1"})
MERGE (cst:Constraint {id:"CST_BASE"}) 
  ON CREATE SET cst.type="General", cst.description="System-wide constraints"
MERGE (f)-[:HAS_CONSTRAINT]->(cst)
MERGE (p)-[:HAS_CONSTRAINT]->(cst);

// --- SECURITY QS
MATCH (p:Project {id:"P1"}), (f:Feature {id:"F1"})
MERGE (cst:Constraint {id:"CST_SEC"}) 
  ON CREATE SET cst.type="Security", cst.description="Protect against brute-force attacks"
MERGE (qs:Qual_Scenario {id:"QS_SEC"})
  ON CREATE SET qs.source="Attacker",
                qs.stimulus="Multiple failed login attempts",
                qs.environment="Normal operation",
                qs.artefact="Authentication system",
                qs.response="Lock account",
                qs.response_measure="Account locked within 1 second"
MERGE (f)-[:HAS_CONSTRAINT]->(cst)
MERGE (qs)-[:SATISFIES]->(cst)
MERGE (p)-[:HAS_QUAL_SCENARIO]->(qs);

// --- PERFORMANCE QS
MATCH (p:Project {id:"P1"}), (f:Feature {id:"F1"})
MERGE (cst:Constraint {id:"CST_PERF"}) 
  ON CREATE SET cst.type="Performance", cst.description="Handle peak traffic"
MERGE (qs:Qual_Scenario {id:"QS_PERF"})
  ON CREATE SET qs.source="User",
                qs.stimulus="1000 concurrent login requests",
                qs.environment="Peak load",
                qs.artefact="Authentication service",
                qs.response="System authenticates requests",
                qs.response_measure="95% requests within 2 seconds"
MERGE (f)-[:HAS_CONSTRAINT]->(cst)
MERGE (qs)-[:SATISFIES]->(cst)
MERGE (p)-[:HAS_QUAL_SCENARIO]->(qs);

// --- USABILITY QS
MATCH (p:Project {id:"P1"}), (f:Feature {id:"F1"})
MERGE (cst:Constraint {id:"CST_USA"}) 
  ON CREATE SET cst.type="Usability", cst.description="Ease of use"
MERGE (qs:Qual_Scenario {id:"QS_USA"})
  ON CREATE SET qs.source="New user",
                qs.stimulus="First login attempt",
                qs.environment="Normal operation",
                qs.artefact="UI Login Page",
                qs.response="User successfully logs in without guidance",
                qs.response_measure="≥ 90% success rate in usability test"
MERGE (f)-[:HAS_CONSTRAINT]->(cst)
MERGE (qs)-[:SATISFIES]->(cst)
MERGE (p)-[:HAS_QUAL_SCENARIO]->(qs);

// --- SCALABILITY QS
MATCH (p:Project {id:"P1"}), (f:Feature {id:"F1"})
MERGE (cst:Constraint {id:"CST_SCA"}) 
  ON CREATE SET cst.type="Scalability", cst.description="System scales horizontally"
MERGE (qs:Qual_Scenario {id:"QS_SCA"})
  ON CREATE SET qs.source="System monitor",
                qs.stimulus="Traffic doubles",
                qs.environment="Cloud deployment",
                qs.artefact="Backend service cluster",
                qs.response="System auto-scales by adding nodes",
                qs.response_measure="Scaling completed within 5 minutes"
MERGE (f)-[:HAS_CONSTRAINT]->(cst)
MERGE (qs)-[:SATISFIES]->(cst)
MERGE (p)-[:HAS_QUAL_SCENARIO]->(qs);

// --------------------------------------------------
// ARTIFACT
// --------------------------------------------------
MATCH (p:Project {id:"P1"}), (f:Feature {id:"F1"}), (s:Stakeholder {id:"S1"})
MERGE (a:Artifact {id:"A1"})
  ON CREATE SET a.type="Specification", a.name="API Spec"
MERGE (f)-[:PRODUCES]->(a)
MERGE (a)-[:USED_BY]->(s)
MERGE (p)-[:HAS_ARTIFACT]->(a);

// --------------------------------------------------
// DECISION
// --------------------------------------------------
MATCH (p:Project {id:"P1"}), (s:Stakeholder {id:"S1"}), (f:Feature {id:"F1"})
MERGE (d:Decision {id:"D1"})
  ON CREATE SET d.description="Chose OAuth2 over SAML", d.date="2025-01-15"
MERGE (d)-[:MADE_BY]->(s)
MERGE (d)-[:AFFECTS]->(f)
MERGE (p)-[:HAS_DECISION]->(d);

// --------------------------------------------------
// GOAL + PRIORITY
// --------------------------------------------------
MATCH (p:Project {id:"P1"}), (s:Stakeholder {id:"S1"}), (f:Feature {id:"F1"})
MERGE (gq:Goal_Quotation {id:"GQ1"}) 
  ON CREATE SET gq.text="System must be secure"
MERGE (pl:Priority_Level {id:"PL1"}) ON CREATE SET pl.value="High"
MERGE (g:Goal {id:"G1"}) ON CREATE SET g.description="Secure Authentication"
MERGE (g)-[:HAS_PRIORITY]->(pl)
MERGE (s)-[:STATES]->(gq)
MERGE (gq)-[:EXPRESSES]->(g)
MERGE (g)-[:SUPPORTED_BY]->(f)
MERGE (g)-[:OWNED_BY]->(s)
MERGE (p)-[:HAS_GOAL]->(g);

// --------------------------------------------------
// KPI & EVALUATION
// --------------------------------------------------
MATCH (p:Project {id:"P1"}), (g:Goal {id:"G1"})
MERGE (k:KPI {id:"K1"}) ON CREATE SET k.metric="time_to_market"
MERGE (k)-[:MEASURES]->(g);

MATCH (p:Project {id:"P1"})
MERGE (eval:Evaluation {id:"E1"}) 
  ON CREATE SET eval.date="2025-12-31", eval.result="Met"
MERGE (eval)-[:EVALUATES]->(p);

// --------------------------------------------------
// TIMELINE & MILESTONE
// --------------------------------------------------
MATCH (p:Project {id:"P1"})
MERGE (t:Timeline {id:"T1"}) SET t.start_date="2025-01-01", t.end_date="2025-12-31"
MERGE (p)-[:HAS_TIMELINE]->(t);

MATCH (p:Project {id:"P1"})
MERGE (m:Milestone {id:"M1"}) SET m.name="MVP Release", m.date="2025-09-01"
MERGE (p)-[:HAS_MILESTONE]->(m);

// --------------------------------------------------
// TASKS
// --------------------------------------------------
MATCH (p:Project {id:"P1"}), (f:Feature {id:"F1"})
MERGE (t1:Task {id:"TSK1"}) ON CREATE SET t1.name="Design Login Page"
MERGE (t2:Task {id:"TSK2"}) ON CREATE SET t2.name="Implement OAuth2"
MERGE (t2)-[:DEPENDS_ON]->(t1)
MERGE (f)-[:IMPLEMENTED_BY]->(t1)
MERGE (f)-[:IMPLEMENTED_BY]->(t2)
MERGE (p)-[:HAS_TASK]->(t1)
MERGE (p)-[:HAS_TASK]->(t2);

// --------------------------------------------------
// CONTEXT (Business/Technical/Adjacent Systems)
// --------------------------------------------------
MATCH (p:Project {id:"P1"})
MERGE (ctx:Context {id:"CTX1"})
MERGE (bus:Business {id:"BIZ1"}) SET bus.description="Banking regulations"
MERGE (tech:Technical {id:"TECH1"}) SET tech.description="Encryption required"
MERGE (adj:Adjacent_System {id:"AS1"}) SET adj.description="Payment Gateway", adj.owner="External Partner"
MERGE (ctx)-[:CAN_BE]->(bus)
MERGE (ctx)-[:CAN_BE]->(tech)
MERGE (ctx)-[:INTERFACES_WITH]->(adj)
MERGE (p)-[:OPERATES_IN]->(ctx);

// --------------------------------------------------
// INPUT & OUTPUT
// --------------------------------------------------
MATCH (p:Project {id:"P1"}), (adj:Adjacent_System {id:"AS1"})
MERGE (inp:Input_From_Product {id:"INP1"}) SET inp.type="Login Request"
MERGE (out:Output_From_Product {id:"OUT1"}) SET out.type="Access Token"
MERGE (adj)-[:RECEIVES]->(inp)
MERGE (adj)-[:SENDS]->(out);
