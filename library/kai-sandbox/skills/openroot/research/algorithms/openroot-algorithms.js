'use strict';
const PHI = 1.6180339887;
const THERMAL_COP = 8.544;
const THERMAL_IN_W = 931;
const THERMAL_OUT_W = 2197;
const CURE_DAYS = 21;

function fullerCoefficient({ P, R, A, E, C, T }) {
  if (E <= 0 || C <= 0 || T <= 0) throw new Error('Denominators must be > 0');
  return Math.round((P * R * A) / (E * C * T) * 100) / 100;
}

function leastAmongYouWeight({ incomePercentile=0.5, accessToGrid=0.5, accessToCleanWater=0.5, accessToHealthcare=0.5, conflictZone=0 }) {
  const d = (1-incomePercentile)*0.30 + (1-accessToGrid)*0.20 + (1-accessToCleanWater)*0.25 + (1-accessToHealthcare)*0.15 + conflictZone*0.10;
  return 1.0 + d * 2.0;
}

function priorityScore(fullerParams, populationParams) {
  const epsilon = fullerCoefficient(fullerParams);
  const lambda  = leastAmongYouWeight(populationParams);
  const priority = Math.round(epsilon * lambda * 100) / 100;
  let tier;
  if (priority >= 2000) tier = 'CRITICAL — deploy immediately';
  else if (priority >= 800) tier = 'HIGH — next node target';
  else if (priority >= 300) tier = 'MEDIUM — bounty board active';
  else tier = 'LOW — future roadmap';
  return { epsilon, lambda, priority, tier };
}

function lordsPlayerDirective(proposal) {
  const violations = [], passes = [];
  if (proposal.producesPhysicalValue) passes.push('✓ Produces real material good');
  else violations.push('✗ No physical value produced');
  if (proposal.hasPatents || proposal.isClosedSource) violations.push('✗ CRITICAL: Patents/closed source — violates covenant');
  else passes.push('✓ Open license — knowledge belongs to all');
  if (proposal.weaponApplication || proposal.surveillanceApplication) violations.push('✗ CRITICAL: Weapon/surveillance use — refused');
  else passes.push('✓ No harmful application');
  if (proposal.requiresFounderToOperate) violations.push('✗ Requires founder — not self-sustaining yet');
  else passes.push('✓ Operable without founder');
  if (proposal.errorsPubliclyCorrectible) passes.push('✓ Errors public and correctable');
  else violations.push('✗ No public error correction');
  const approved = violations.filter(v => v.includes('CRITICAL')).length === 0;
  return { approved, passes, violations, verdict: approved ? 'APPROVED' : 'BLOCKED' };
}

function aegisMeshExpand(origin, ringNumber, baseRadiusKm=80) {
  const nodes = [];
  const ringRadius = baseRadiusKm * Math.pow(PHI, ringNumber - 1);
  const nodeCount = 6 * ringNumber;
  const angleStep = (2 * Math.PI) / nodeCount;
  const rotOffset = ringNumber % 2 === 0 ? angleStep / 2 : 0;
  for (let i = 0; i < nodeCount; i++) {
    const angle = i * angleStep + rotOffset;
    const dLat = (ringRadius / 111.32) * Math.cos(angle);
    const dLon = (ringRadius / (111.32 * Math.cos(origin.lat * Math.PI / 180))) * Math.sin(angle);
    nodes.push({ id:`${origin.id}-R${ringNumber}N${i+1}`, lat:origin.lat+dLat, lon:origin.lon+dLon, ring:ringNumber, radiusKm:ringRadius, phiScale:Math.pow(PHI,ringNumber-1), status:'undeployed' });
  }
  return nodes;
}

function aegisFullMesh(rings=3) {
  const nodeZero = { id:'NODE-ZERO', lat:36.8767, lon:-89.5882, ring:0, parentId:null, mission:'OpenRoot origin — Sikeston MO', status:'active' };
  const mesh = { nodeZero, rings:{} };
  for (let r=1; r<=rings; r++) mesh.rings[r] = aegisMeshExpand(nodeZero, r);
  mesh.totalNodes = 1 + Object.values(mesh.rings).reduce((s,r)=>s+r.length,0);
  mesh.selfSimilarityIndex = PHI;
  return mesh;
}

function validateThermalLoop(design) {
  const errors=[], warnings=[];
  if (!design.wetCureDays || design.wetCureDays < CURE_DAYS) errors.push(`FAIL: Wet cure must be ${CURE_DAYS} days. Got: ${design.wetCureDays}`);
  if (design.desiccantPosition !== 'intake') errors.push('FAIL: Desiccant must be at fresh air intake — before labyrinth');
  if (!design.tunnelFilledSolid) errors.push('FAIL: Tunnel must be FILLED SOLID with open-cell aerocement');
  if (!design.twoSeparateTanks) errors.push('FAIL: Must have TWO separate tanks — A (hot) and B (cold)');
  if (design.claimsThermodynamicEfficiencyOver100) errors.push('FAIL: Never claim >100% thermodynamic efficiency');
  return { valid:errors.length===0, errors, warnings, expectedOutput:`${THERMAL_IN_W}W in → ${THERMAL_OUT_W}W out at COP ${THERMAL_COP}` };
}

function goldenRuleFilter(action) {
  if (action.extractsValueWithoutReturn) return { proceed:false, reason:'Extracts value without return — violates Golden Rule' };
  if (!action.transparentToAffected) return { proceed:false, reason:'Not transparent to those affected — violates Golden Rule' };
  return { proceed:true, reason:'Passes Golden Rule filter', reversible:action.reversible||false };
}

function lostSheepSearch(communities) {
  const lost = communities.filter(c=>!c.hasService).sort((a,b)=>leastAmongYouWeight(b.population||{})-leastAmongYouWeight(a.population||{}));
  return { total:communities.length, served:communities.filter(c=>c.hasService).length, lost:lost.length, searchOrder:lost.map((c,i)=>({ rank:i+1, name:c.name, lambda:leastAmongYouWeight(c.population||{}) })) };
}

function talentsMultiplier(skill, timesShared, nodesReached) {
  if (!skill.isPubliclyShared) return { value:0, warning:'Buried talent — no multiplication. Share openly.' };
  const compounded = skill.baseValue * Math.pow(PHI, Math.log2(timesShared+1));
  const total = compounded * nodesReached;
  return { compoundedValue:Math.round(compounded*100)/100, totalImpact:Math.round(total*100)/100, acreMinted:Math.round(total*10) };
}

const PROJECTS = [
  { name:'Water Purification',      fuller:{P:0.95,R:0.90,A:0.95,E:0.05,C:0.04,T:0.08}, pop:{incomePercentile:0.08,accessToGrid:0.1,accessToCleanWater:0.0,accessToHealthcare:0.1,conflictZone:0} },
  { name:'AeroCement/Thermal Loop', fuller:{P:0.92,R:0.95,A:0.88,E:0.12,C:0.08,T:0.15}, pop:{incomePercentile:0.15,accessToGrid:0.2,accessToCleanWater:0.3,accessToHealthcare:0.2,conflictZone:0} },
  { name:'Refrigeration Unit',      fuller:{P:0.88,R:0.85,A:0.82,E:0.10,C:0.10,T:0.12}, pop:{incomePercentile:0.20,accessToGrid:0.15,accessToCleanWater:0.4,accessToHealthcare:0.25,conflictZone:0} },
  { name:'AEGIS Mesh Protocol',     fuller:{P:0.82,R:0.98,A:0.85,E:0.08,C:0.06,T:0.10}, pop:{incomePercentile:0.30,accessToGrid:0.1,accessToCleanWater:0.5,accessToHealthcare:0.3,conflictZone:0} },
  { name:'Stirling Scooter',        fuller:{P:0.75,R:0.80,A:0.70,E:0.18,C:0.20,T:0.20}, pop:{incomePercentile:0.25,accessToGrid:0.3,accessToCleanWater:0.5,accessToHealthcare:0.35,conflictZone:0} },
  { name:'Power Plant (Stirling)',   fuller:{P:0.70,R:0.60,A:0.55,E:0.30,C:0.40,T:0.35}, pop:{incomePercentile:0.35,accessToGrid:0.0,accessToCleanWater:0.5,accessToHealthcare:0.4,conflictZone:0} },
];

function runPriorityRanking() {
  const results = PROJECTS.map(p=>({ name:p.name, ...priorityScore(p.fuller, p.pop) })).sort((a,b)=>b.priority-a.priority);
  console.log('\n╔══════════════════════════════════════════════════════════════╗');
  console.log('║  OPENROOT — Fuller Ε × Christ λ = Priority Π               ║');
  console.log('╠══════════════════════════════════════════════════════════════╣');
  results.forEach((r,i) => {
    console.log(`║ ${i+1}. ${r.name.padEnd(24)} Ε:${String(r.epsilon).padStart(8)}  λ:${r.lambda.toFixed(2)}  Π:${String(r.priority).padStart(9)} ║`);
    console.log(`║    → ${r.tier.padEnd(57)}║`);
    console.log('╠══════════════════════════════════════════════════════════════╣');
  });
  console.log('╚══════════════════════════════════════════════════════════════╝');
}

function runAegisMeshDemo() {
  const mesh = aegisFullMesh(3);
  console.log(`\nAEGIS MESH — Node Zero: Sikeston MO (${mesh.nodeZero.lat}, ${mesh.nodeZero.lon})`);
  console.log(`Total nodes (3 rings): ${mesh.totalNodes}  |  φ: ${mesh.selfSimilarityIndex}`);
  Object.entries(mesh.rings).forEach(([ring,nodes]) => {
    console.log(`  Ring ${ring}: ${nodes.length} nodes  ~${Math.round(nodes[0].radiusKm)}km radius`);
  });
}

module.exports = { fullerCoefficient, leastAmongYouWeight, priorityScore, lordsPlayerDirective, aegisMeshExpand, aegisFullMesh, validateThermalLoop, goldenRuleFilter, lostSheepSearch, talentsMultiplier, PHI, THERMAL_COP, CURE_DAYS };
if (require.main === module) { runPriorityRanking(); runAegisMeshDemo(); }
