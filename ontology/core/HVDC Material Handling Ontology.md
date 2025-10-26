> **⚠️ 중요**: 이 문서를 읽기 전에 **`../logiontology/`** 폴더를 먼저 확인하세요!
> - **전체 구현 코드**: `../logiontology/src/`
> - **설정 파일**: `../logiontology/configs/`
> - **온톨로지 정의**: `../logiontology/configs/ontology/hvdc_ontology.ttl`
> - **문서**: `../logiontology/README.md`, `../logiontology/CHANGELOG.md`

---

title: "HVDC Material Handling Ontology - Consolidated"
type: "ontology-design"
domain: "material-handling"
sub-domains: ["customs-clearance", "storage-inland-transport", "offshore-marine-transport", "site-receiving", "transformer-handling"]
version: "consolidated-1.0"
date: "2025-10-26"
tags: ["ontology", "hvdc", "material-handling", "workshop", "transformer", "logistics", "consolidated"]
standards: ["RDF", "OWL", "SHACL", "SPARQL", "JSON-LD", "Turtle", "XSD", "IMSBC", "SOLAS", "ADNOC-HSE"]
status: "active"
source_files: ["HVDC_Material Handling Workshop_(20241119_1).pdf"]
hvdc-material-handling · CONSOLIDATED-05
📑 Table of Contents

Overview
Customs Clearance
Storage & Inland Transportation
Offshore Marine Transportation
Site Receiving
Material Handling (Transformer)


Section 1: Overview
Source

Original File: HVDC_Material Handling Workshop_(20241119_1).pdf
Version: unified-1.0
Date: 2024-11-19

Executive Summary
The Material Handling Workshop provides a comprehensive perspective on logistics operations for the Independent Subsea HVDC System Project (Project Lightning) in the UAE. It emphasizes timely overseas and inland transportation of purchased materials, with a focus on customs clearance, port handling, storage, and site offloading. Key entities include ports (Khalifa for containers, Zayed for bulk/heavy cargo, Jebel Ali for special cases), the Mussafah Offshore Supply Base (MOSB) as a central hub, and onshore/offshore sites (MIR, SHU, DAS, AGI). Operations are divided into stages: A (overseas importation) and B (offshore marine transportation via LCT). Compliance with UAE customs regulations, ADNOC HSE standards, and supplier-specific preservation requirements (e.g., Hitachi) is critical.
Visual — Core Classes/Relations (Summary)











































































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:ProjectprojectName, datehasPhase → PhaseWorkshop TitleStatus, Timelinehvdc:PhasephaseType (A/B)involves → Entity (Port, MOSB, Site)Logistics FlowCompletion, Compliancehvdc:Portname, type (Container/Bulk)handles → CargoUAE Port InfoClearance, Handlinghvdc:MOSBareaSqm, operator (ALS)consolidates → Cargo, dispatches → SiteHub OperationsStorage, Loadinghvdc:Sitename, laydownSqm, type (Onshore/Offshore)receives → CargoSite DetailsReceiving, Preservationhvdc:Cargotype, weight, dimstransportedBy → TransportMeansMaterial SpecsCondition, Locationhvdc:TransportMeanstype (LCT/SPMT/Crane)usedIn → OperationTransport ProcessSafety, Efficiencyhvdc:Operationtype (Loading/Unloading)requires → Document/PermitHSE ProceduresApproval, Executionhvdc:Documenttype (BL/PL/MRR)validates → OperationForms/ReportsCompliance, Record
Data Sources: Workshop slides on ports, sites, transport, and procedures.
How it Works (Flow)

Overseas Import (Phase A): Materials arrive at ports → Customs clearance → Port handling → Inland transport to MOSB/Sites.
Offshore Transport (Phase B): Consolidation at MOSB → Loading onto LCT → Marine voyage to islands → Offloading.
Site Receiving: Inspection (MRI/MRR) → Storage/Preservation per classification → Issuance (MRS/MIS).
Transformer Handling: Unloading → Temporary storage → On-foundation via SPMT/Skidding → Preservation checks.


Section 2: Customs Clearance
Source

Original File: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 7-9)
Version: unified-1.0
Date: 2024-11-19

Executive Summary
Customs clearance complies with UAE regulations using eDAS system for document submission. Required documents include BL/AWB, Commercial Invoice, Packing List, Certificate of Origin, and Attestation Invoice. Consignee is Abu Dhabi Offshore Power Transmission Company Limited LLC, with ADNOC/ADOPT codes. For Dubai imports (e.g., Jebel Ali), duty is paid by contractor and reimbursed. Status is shared with ADOPT post-clearance.
Visual — Core Classes/Relations (Summary)

































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:CustomsDeclarationcodeNo, locationuses → DocumenteDAS ProcessApproval, Duty Paymenthvdc:Documenttype (BL/Invoice/PL)submittedTo → System (eDAS)Shipping DocsValidation, Endorsementhvdc:Consigneename, codeendorses → BLADOPT StampsDelivery Plan
How it Works (Flow)

Shipping Documents: Prepare BL, Invoice, PL, CO.
eDAS System: Submit Attestation Invoice for customs approval.
BL Endorsement: ADOPT stamps (consignee: ADOPT).
Customs Declaration: Submit docs for clearance.
Delivery: Plan transportation post-clearance.


Section 3: Storage & Inland Transportation
Source

Original File: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 10-14)
Version: unified-1.0
Date: 2024-11-19

Executive Summary
Storage follows Material Management Control Procedure, with classifications (Annex J) and supplier guidelines (e.g., Hitachi: Indoor +5° to +40°C, RH ≤85%). Indoor warehouses near MIR/SHU (6,000-8,000 sqm) for sensitive materials. Laydowns at sites: MIR (35,006 sqm), SHU (10,556 sqm), DAS (35,840 sqm), AGI (47,198 sqm). Inland transport for heavy equipment (>90t) requires DOT permit. Process includes unloading, storage on stools/beams, and preservation.
Visual — Core Classes/Relations (Summary)

































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:Storagetype (Indoor/Outdoor), areaSqmfollows → ProcedureStorage StandardsPreservation, Locationhvdc:LaydownsiteName, sqmhosts → CargoSite LaydownsCompaction, Setuphvdc:InlandTransportpermit (DOT), time (Night)transports → CargoHeavy Equip ProcessDelivery, Safety
How it Works (Flow)

Storage Classification: Assign per Annex J/Hitachi recs.
Locations: Designate indoor/outdoor yards, ports, MOSB.
Heavy Transport: Unload vessel → Temp storage → Barge/Inland → Site offload.
Permits: DOT for >90t, police approval.


Section 4: Offshore Marine Transportation
Source

Original File: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 15-18)
Version: unified-1.0
Date: 2024-11-19

Executive Summary
Operated by ADNOC L&S at MOSB, complying with Offshore HSE standards. Process: Gate pass → Planning/docs → Operation (LOLO/RORO) → Exit pass. Voyage times: MOSB-DAS (20 hrs), MOSB-AGI (10 hrs). Involves inspections, crane/forklift requests, and coordination for offloading at islands.
Visual — Core Classes/Relations (Summary)

































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:MarineTransportvoyageTime, vessel (LCT)compliesWith → HSEStandardsALS ProceduresSafety, Timelinesshvdc:OperationStepstepNo, focalPointrequires → Document/PermitFlow StepsExecution, Approvalhvdc:Inspectiontype (Lifting)validates → CargoSafety ChecksCompliance
How it Works (Flow)

Gate Pass: Documents for entry/exit.
Planning: PL, certificates, scheduling.
Operation: Request equipment, lashing.
Shipping: Priority plan, PL to islands.
Voyage: LCT transport, safety priority.


Section 5: Site Receiving
Source

Original File: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 19-29)
Version: unified-1.0
Date: 2024-11-19

Executive Summary
Follows Material Management Control Procedure. Includes delivery planning, HSE safety (PTW, FRA), material receiving (MRR/MRI/ITP/MAR), OSD reports for discrepancies, request/issuance slips (MRS/MIS), storage/preservation (indoor/outdoor guidelines), and forms/checklists.
Visual — Core Classes/Relations (Summary)

































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:Receivingtype (Good/OSD)requires → InspectionProceduresAcceptance, Reporthvdc:RequestSliptype (MRS/MIS)approves → TeamFormsIssuance, Acknowledgmenthvdc:Preservationguidelines (Temp/RH)appliesTo → CargoStorage InstructionsCondition Maintenance
How it Works (Flow)

Delivery Plan: Supplier provides PL, ETA; SCT prepares equipment.
HSE: PTW, TBT, hazard assessment.
Receiving: Check vs PL, issue MRR if good; OSD if not.
Inspection: Joint with OE, attach docs (MRI/ITP/MAR).
Issuance: MRS approval → MIS → Physical check.
Storage: Follow manufacturer guidelines (e.g., covered tarpaulin).


Section 6: Material Handling (Transformer)
Source

Original File: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 30-42)
Version: unified-1.0
Date: 2024-11-19

Executive Summary
Transformer schedules for DAS/Zakum clusters detailed by ETD/ETA/port/on-site dates. On-shore (MIR/SHU): Unload vessel → Temp storage → Inland transport (DOT permit). Off-shore (DAS/AGI): SPMT loading → LCT roll-on → Sea fastening. Preparations: PTWs, risk assessments, stability calcs, mooring plans. Site receiving: Survey, compaction, jackdown. Preservation: Impact recorder checks, dry air/N2 gas top-up. On-foundation: Skidding method post-building completion.
Visual — Core Classes/Relations (Summary)

































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:TransformerunitNo, ETD/ETAtransportedBy → Means (SPMT/LCT)SchedulesDelivery, Installationhvdc:Proceduretype (Top-Up/On-Foundation)requires → Equipment/DocumentProcessesSafety, Executionhvdc:PreservationCheckgaugeLevel, gasTypeperformsOn → TransformerChecksMaintenance
How it Works (Flow)

Schedules: Origin (Sweden/Brazil), ports (Mugharraq/Zayed).
On-Shore: Unload crane → SPMT → Storage (stools/beams) → Inland (night, permits).
Off-Shore: Lift to SPMT → Roll-on LCT (mats/stools) → Sea fastening.
Preparations: PTWs, calcs (RoRo ramp, ballast, mooring).
Receiving: Site survey, jackdown under supervision.
Preservation: Impact recorder test, gauge checks, gas top-up.
On-Foundation: Mobilize SPMT/skidding/jacking → Sequence: Position, jackup, skid.


Integrated Ontology System
Domain Ontology
Core Classes
turtle@prefix hvdc: <https://hvdc-project.com/ontology/material-handling/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

hvdc:Project a owl:Class ;
    rdfs:label "Project" ;
    rdfs:comment "Represents the HVDC project entity." .

hvdc:Phase a owl:Class ;
    rdfs:label "Phase" ;
    rdfs:comment "Logistics phases (A: Import, B: Offshore)." .

hvdc:Port a owl:Class ;
    rdfs:label "Port" ;
    rdfs:comment "Ports for cargo arrival." .

hvdc:MOSB a owl:Class ;
    rdfs:label "MOSB" ;
    rdfs:comment "Mussafah Offshore Supply Base." .

hvdc:Site a owl:Class ;
    rdfs:label "Site" ;
    rdfs:comment "Onshore/Offshore sites." .

hvdc:Cargo a owl:Class ;
    rdfs:label "Cargo" ;
    rdfs:comment "Materials being handled." .

hvdc:TransportMeans a owl:Class ;
    rdfs:label "Transport Means" ;
    rdfs:comment "Vessels, trailers, etc." .

hvdc:Operation a owl:Class ;
    rdfs:label "Operation" ;
    rdfs:comment "Handling operations." .

hvdc:Document a owl:Class ;
    rdfs:label "Document" ;
    rdfs:comment "Required documents and forms." .
Core Properties
turtlehvdc:hasPhase a owl:ObjectProperty ;
    rdfs:domain hvdc:Project ;
    rdfs:range hvdc:Phase .

hvdc:involves a owl:ObjectProperty ;
    rdfs:domain hvdc:Phase ;
    rdfs:range [ owl:unionOf (hvdc:Port hvdc:MOSB hvdc:Site) ] .

hvdc:handles a owl:ObjectProperty ;
    rdfs:domain hvdc:Port ;
    rdfs:range hvdc:Cargo .

hvdc:consolidates a owl:ObjectProperty ;
    rdfs:domain hvdc:MOSB ;
    rdfs:range hvdc:Cargo .

hvdc:dispatches a owl:ObjectProperty ;
    rdfs:domain hvdc:MOSB ;
    rdfs:range hvdc:Site .

hvdc:receives a owl:ObjectProperty ;
    rdfs:domain hvdc:Site ;
    rdfs:range hvdc:Cargo .

hvdc:transportedBy a owl:ObjectProperty ;
    rdfs:domain hvdc:Cargo ;
    rdfs:range hvdc:TransportMeans .

hvdc:usedIn a owl:ObjectProperty ;
    rdfs:domain hvdc:TransportMeans ;
    rdfs:range hvdc:Operation .

hvdc:requires a owl:ObjectProperty ;
    rdfs:domain hvdc:Operation ;
    rdfs:range hvdc:Document .

hvdc:projectName a owl:DatatypeProperty ;
    rdfs:domain hvdc:Project ;
    rdfs:range xsd:string .

hvdc:date a owl:DatatypeProperty ;
    rdfs:domain hvdc:Project ;
    rdfs:range xsd:date .

hvdc:phaseType a owl:DatatypeProperty ;
    rdfs:domain hvdc:Phase ;
    rdfs:range xsd:string .

hvdc:name a owl:DatatypeProperty ;
    rdfs:domain [ owl:unionOf (hvdc:Port hvdc:Site) ] ;
    rdfs:range xsd:string .

hvdc:type a owl:DatatypeProperty ;
    rdfs:domain [ owl:unionOf (hvdc:Port hvdc:Site hvdc:Cargo hvdc:TransportMeans hvdc:Operation hvdc:Document) ] ;
    rdfs:range xsd:string .

hvdc:areaSqm a owl:DatatypeProperty ;
    rdfs:domain [ owl:unionOf (hvdc:MOSB hvdc:Site) ] ;
    rdfs:range xsd:decimal .

hvdc:weight a owl:DatatypeProperty ;
    rdfs:domain hvdc:Cargo ;
    rdfs:range xsd:decimal .

hvdc:dims a owl:DatatypeProperty ;
    rdfs:domain hvdc:Cargo ;
    rdfs:range xsd:string .

hvdc:voyageTime a owl:DatatypeProperty ;
    rdfs:domain hvdc:MarineTransport ;
    rdfs:range xsd:integer .
SHACL Constraints
turtlehvdc:ProjectShape a sh:NodeShape ;
    sh:targetClass hvdc:Project ;
    sh:property [
        sh:path hvdc:projectName ;
        sh:minCount 1 ;
        sh:message "Project must have a name."
    ] ;
    sh:property [
        sh:path hvdc:date ;
        sh:minCount 1 ;
        sh:message "Project must have a date."
    ] .

hvdc:PhaseShape a sh:NodeShape ;
    sh:targetClass hvdc:Phase ;
    sh:property [
        sh:path hvdc:phaseType ;
        sh:in ("A" "B") ;
        sh:message "Phase type must be A or B."
    ] .

hvdc:PortShape a sh:NodeShape ;
    sh:targetClass hvdc:Port ;
    sh:property [
        sh:path hvdc:name ;
        sh:minCount 1 ;
        sh:message "Port must have a name."
    ] ;
    sh:property [
        sh:path hvdc:type ;
        sh:in ("Container" "Bulk" "Special") ;
        sh:message "Port type must be Container, Bulk, or Special."
    ] .

hvdc:MOSBShape a sh:NodeShape ;
    sh:targetClass hvdc:MOSB ;
    sh:property [
        sh:path hvdc:areaSqm ;
        sh:minInclusive 20000.0 ;
        sh:message "MOSB area must be at least 20,000 sqm."
    ] .

hvdc:SiteShape a sh:NodeShape ;
    sh:targetClass hvdc:Site ;
    sh:property [
        sh:path hvdc:name ;
        sh:minCount 1 ;
        sh:message "Site must have a name."
    ] ;
    sh:property [
        sh:path hvdc:type ;
        sh:in ("Onshore" "Offshore") ;
        sh:message "Site type must be Onshore or Offshore."
    ] ;
    sh:property [
        sh:path hvdc:areaSqm ;
        sh:minInclusive 10000.0 ;
        sh:message "Site laydown area must be at least 10,000 sqm."
    ] .

hvdc:CargoShape a sh:NodeShape ;
    sh:targetClass hvdc:Cargo ;
    sh:property [
        sh:path hvdc:type ;
        sh:minCount 1 ;
        sh:message "Cargo must have a type."
    ] ;
    sh:property [
        sh:path hvdc:weight ;
        sh:minInclusive 0.01 ;
        sh:message "Weight must be positive."
    ] .

hvdc:TransportMeansShape a sh:NodeShape ;
    sh:targetClass hvdc:TransportMeans ;
    sh:property [
        sh:path hvdc:type ;
        sh:minCount 1 ;
        sh:message "Transport means must have a type."
    ] .

hvdc:OperationShape a sh:NodeShape ;
    sh:targetClass hvdc:Operation ;
    sh:property [
        sh:path hvdc:type ;
        sh:minCount 1 ;
        sh:message "Operation must have a type."
    ] .

hvdc:DocumentShape a sh:NodeShape ;
    sh:targetClass hvdc:Document ;
    sh:property [
        sh:path hvdc:type ;
        sh:minCount 1 ;
        sh:message "Document must have a type."
    ] .
JSON-LD Examples
Project Example
json{
  "@context": {
    "hvdc": "https://hvdc-project.com/ontology/material-handling/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  },
  "@id": "hvdc:project-lightning",
  "@type": "hvdc:Project",
  "hvdc:projectName": "Independent Subsea HVDC System Project (Project Lightning)",
  "hvdc:date": "2024-11-19",
  "hvdc:hasPhase": [
    {
      "@type": "hvdc:Phase",
      "hvdc:phaseType": "A",
      "hvdc:involves": [
        {"@id": "hvdc:port-khalifa"},
        {"@id": "hvdc:port-zayed"}
      ]
    },
    {
      "@type": "hvdc:Phase",
      "hvdc:phaseType": "B",
      "hvdc:involves": [
        {"@id": "hvdc:mosb"},
        {"@id": "hvdc:site-das"}
      ]
    }
  ]
}
Transformer Handling Example
json{
  "@context": {
    "hvdc": "https://hvdc-project.com/ontology/material-handling/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  },
  "@id": "hvdc:transformer-das-1",
  "@type": "hvdc:Cargo",
  "hvdc:type": "Transformer",
  "hvdc:weight": 200.0,
  "hvdc:dims": "L:10m W:5m H:6m",
  "hvdc:transportedBy": {
    "@type": "hvdc:TransportMeans",
    "hvdc:type": "SPMT"
  },
  "hvdc:requires": {
    "@type": "hvdc:Document",
    "hvdc:type": "PTW"
  }
}
SPARQL Queries
Project Phases Query
sparqlPREFIX hvdc: <https://hvdc-project.com/ontology/material-handling/>

SELECT ?phaseType ?entityId
WHERE {
    ?project hvdc:hasPhase ?phase .
    ?phase hvdc:phaseType ?phaseType ;
           hvdc:involves ?entity .
    ?entity @id ?entityId .
}
ORDER BY ?phaseType
Cargo Transport Query
sparqlPREFIX hvdc: <https://hvdc-project.com/ontology/material-handling/>

SELECT ?cargoType ?transportType ?documentType
WHERE {
    ?cargo hvdc:type ?cargoType ;
           hvdc:transportedBy ?means .
    ?means hvdc:type ?transportType .
    OPTIONAL { ?cargo hvdc:requires ?doc . ?doc hvdc:type ?documentType . }
}
ORDER BY ?cargoType
Semantic KPI Layer
Material Handling KPIs

Delivery Timeliness: OTIF (On-Time In-Full) rate.
Preservation Compliance: Adherence to temp/RH guidelines.
Safety Incident Rate: Zero incidents in handling operations.
Permit Approval Time: SLA for DOT/PTW.

Transport KPIs

Voyage Efficiency: Actual vs. planned transit times.
Load Utilization: LCT deck usage percentage.
Inspection Pass Rate: First-time approvals.

Recommended Commands

/material-handling analyze --phase=A [Import stage analysis]
/customs-clearance verify --docs [Document validation]
/storage-plan optimize --site=MIR [Laydown optimization]
/marine-transport schedule --voyage [LCT scheduling]
/site-receiving inspect --cargo [MRI/MRR generation]
/transformer-handle preserve --check [Gauge/preservation checks]

This consolidated ontology integrates the Material Handling Workshop content into a knowledge graph for the HVDC project, enhancing data consistency, traceability, and automation in logistics operations.18.4sIntegrate with bulk cargo ontologyThought for 19s
title: "HVDC Material Handling & Bulk Cargo Ontology - Integrated"
type: "ontology-design"
domain: "material-handling-bulk-cargo"
sub-domains: ["customs-clearance", "storage-inland-transport", "offshore-marine-transport", "site-receiving", "transformer-handling", "bulk-cargo-operations", "seafastening", "stability-control"]
version: "integrated-1.0"
date: "2025-10-26"
tags: ["ontology", "hvdc", "material-handling", "bulk-cargo", "workshop", "transformer", "logistics", "integrated"]
standards: ["RDF", "OWL", "SHACL", "SPARQL", "JSON-LD", "Turtle", "XSD", "IMSBC", "SOLAS", "ADNOC-HSE"]
status: "active"
source_files: ["HVDC_Material Handling Workshop_(20241119_1).pdf", "1_CORE-05-hvdc-bulk-cargo-ops.md"]
hvdc-material-handling-bulk · INTEGRATED-06
📑 Table of Contents

Overview
Customs Clearance
Storage & Inland Transportation
Offshore Marine Transportation
Site Receiving
Material Handling (Transformer)
Bulk Cargo Operations


Section 1: Overview
Sources

Material Handling: HVDC_Material Handling Workshop_(20241119_1).pdf
Bulk Cargo: 1_CORE-05-hvdc-bulk-cargo-ops.md
Version: integrated-1.0
Date: 2025-10-26

Executive Summary
This integrated ontology combines the material handling processes from the HVDC workshop with the bulk cargo operations ontology, creating a unified knowledge graph for the Independent Subsea HVDC System Project (Project Lightning) in the UAE. It encompasses overseas importation (Phase A), offshore marine transportation (Phase B), and detailed bulk cargo handling, including planning, loading, discharging, stowage, lashing, stability control, and lifting. Key entities include ports, MOSB hub, sites, cargo types (e.g., transformers, steel structures, OOG), and transport means (e.g., LCT, SPMT). Compliance with UAE customs, ADNOC HSE, IMSBC, SOLAS, and supplier preservation standards (e.g., Hitachi) is enforced. The integration aligns classes and relations to support end-to-end traceability, automation, and risk management for bulk and project cargo.
Visual — Core Classes/Relations (Summary)











































































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:ProjectprojectName, datehasPhase → PhaseWorkshop Title, Bulk PlanningStatus, Timelinehvdc:PhasephaseType (A/B)involves → Entity (Port, MOSB, Site)Logistics Flow, Operation PhasesCompletion, Compliancehvdc:Portname, type (Container/Bulk)handles → CargoUAE Port InfoClearance, Handlinghvdc:MOSBareaSqm, operator (ALS)consolidates → Cargo, dispatches → SiteHub OperationsStorage, Loadinghvdc:Sitename, laydownSqm, type (Onshore/Offshore)receives → CargoSite DetailsReceiving, Preservationhvdc:Cargotype, weight(t), dims(m), cogX/Y/Z(m), stackable(boolean)transportedBy → TransportMeans, placedOn → DeckArea, securedBy → LashingAssemblyMaterial Specs, Bulk CargoCondition, Location, Stabilityhvdc:TransportMeanstype (LCT/SPMT/Crane), vesselName, imo?usedIn → OperationTransport Process, Vessel RegistrySafety, Efficiencyhvdc:Operationtype (Loading/Unloading/Lifting), status, start/end(DateTime)requires → Document/Permit, uses → EquipmentHSE Procedures, OperationTaskApproval, Executionhvdc:Documenttype (BL/PL/MRR), version, fileRefvalidates → Operation, documents → (Plan/Report)Forms/Reports, Document StoreCompliance, Record
Data Sources: Workshop slides, bulk cargo ontology definitions.
How it Works (Flow)

Overseas Import (Phase A): Materials arrive at ports → Customs clearance → Port handling → Inland transport to MOSB/Sites.
Offshore Transport (Phase B): Consolidation at MOSB → Loading onto LCT (planning, stowage, lashing) → Marine voyage (stability control) → Offloading (lifting, discharging).
Site Receiving: Inspection (MRI/MRR) → Storage/Preservation per classification → Issuance (MRS/MIS).
Bulk Cargo Integration: Data collection → Draft plans (loading, lashing, stability) → Execution (QC checks) → Post-operation (surveys, reports).
Transformer Handling: Unloading → Temporary storage → On-foundation via SPMT/Skidding → Preservation checks, aligned with bulk lashing/stability.


Section 2: Customs Clearance
Source

Material Handling: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 7-9)
Integration Note: Aligns with bulk cargo documentation requirements (e.g., BL for stowage planning).

Executive Summary
Customs clearance adheres to UAE regulations via the eDAS system, requiring documents such as BL/AWB, Commercial Invoice, Packing List, Certificate of Origin, and Attestation Invoice. The consignee is Abu Dhabi Offshore Power Transmission Company Limited LLC, utilizing ADNOC/ADOPT codes. For Dubai imports, duties are paid by the contractor and reimbursed. Post-clearance status is shared with ADOPT. Integration with bulk cargo ensures document links to stowage and lashing plans.
Visual — Core Classes/Relations (Summary)


























ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:CustomsDeclarationcodeNo, locationuses → DocumenteDAS ProcessApproval, Duty Paymenthvdc:Documenttype (BL/Invoice/PL)submittedTo → System (eDAS), documents → Plan (Stowage/Lashing)Shipping Docs, Bulk DocumentationValidation, Endorsement
How it Works (Flow)

Shipping Documents: Prepare BL, Invoice, PL, CO.
eDAS System: Submit Attestation Invoice for approval.
BL Endorsement: ADOPT stamps (consignee: ADOPT).
Customs Declaration: Submit docs for clearance.
Delivery & Bulk Link: Plan transportation; link BL to bulk stowage plans.


Section 3: Storage & Inland Transportation
Source

Material Handling: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 10-14)
Integration Note: Incorporates bulk cargo storage constraints (e.g., stackable, hazmatClass).

Executive Summary
Storage complies with Material Management Control Procedure, classifications (Annex J), and supplier guidelines (e.g., Hitachi: Indoor +5° to +40°C, RH ≤85%). Indoor warehouses near MIR/SHU (6,000-8,000 sqm) handle sensitive materials. Site laydowns: MIR (35,006 sqm), SHU (10,556 sqm), DAS (35,840 sqm), AGI (47,198 sqm). Inland transport for heavy items (>90t) requires DOT permits. Integration adds bulk attributes like COG and stackability for storage optimization.
Visual — Core Classes/Relations (Summary)

































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:Storagetype (Indoor/Outdoor), areaSqmfollows → Procedure, hosts → CargoStorage Standards, DeckAreaPreservation, Locationhvdc:LaydownsiteName, sqmhosts → CargoSite LaydownsCompaction, Setuphvdc:InlandTransportpermit (DOT), time (Night)transports → CargoHeavy Equip ProcessDelivery, Safety
How it Works (Flow)

Storage Classification: Assign per Annex J/Hitachi; consider bulk COG/stackable.
Locations: Designate indoor/outdoor yards, ports, MOSB.
Heavy Transport: Unload vessel → Temp storage → Barge/Inland → Site offload.
Permits: DOT for >90t, police approval.


Section 4: Offshore Marine Transportation
Source

Material Handling: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 15-18)
Bulk Cargo: 1_CORE-05-hvdc-bulk-cargo-ops.md
Integration Note: Merges with bulk loading/discharging, lashing, and stability.

Executive Summary
Operated by ADNOC L&S at MOSB, adhering to Offshore HSE, IMSBC, and SOLAS. Process: Gate pass → Planning/docs → Operation (LOLO/RORO) → Exit pass. Voyage times: MOSB-DAS (20 hrs), MOSB-AGI (10 hrs). Integration incorporates bulk elements: stowage/lashing assemblies, stability cases, and environmental factors for seafastening and control.
Visual — Core Classes/Relations (Summary)

































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:MarineTransportvoyageTime, vessel (LCT)compliesWith → HSEStandards, evaluates → StabilityCaseALS Procedures, Stability CalcSafety, Timelinesshvdc:OperationStepstepNo, focalPointrequires → Document/Permit, uses → LashingAssemblyFlow Steps, Lashing CalcExecution, Approvalhvdc:Inspectiontype (Lifting)validates → CargoSafety ChecksCompliance
How it Works (Flow)

Gate Pass: Documents for entry/exit.
Planning: PL, certificates, scheduling; draft stowage/lashing plans.
Operation: Request equipment, lashing; calculate tension/safety factors.
Shipping: Priority plan, PL to islands; stability checks (GM/VCG).
Voyage: LCT transport, safety priority; monitor environment (wind/seaState).


Section 5: Site Receiving
Source

Material Handling: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 19-29)
Integration Note: Links to bulk post-operation surveys and handovers.

Executive Summary
Adheres to Material Management Control Procedure. Includes delivery planning, HSE (PTW, FRA), receiving (MRR/MRI/ITP/MAR), OSD for discrepancies, requests/issuances (MRS/MIS), storage/preservation, and forms. Integration adds bulk survey reports and handover documents.
Visual — Core Classes/Relations (Summary)

































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:Receivingtype (Good/OSD)requires → InspectionProceduresAcceptance, Reporthvdc:RequestSliptype (MRS/MIS)approves → TeamFormsIssuance, Acknowledgmenthvdc:Preservationguidelines (Temp/RH)appliesTo → CargoStorage InstructionsCondition Maintenance
How it Works (Flow)

Delivery Plan: Supplier PL, ETA; prepare equipment.
HSE: PTW, TBT, hazard assessment.
Receiving: Check vs PL, issue MRR if good; OSD if not.
Inspection: Joint with OE, attach docs; bulk surveys.
Issuance: MRS approval → MIS → Physical check.
Storage: Follow guidelines; bulk handover.


Section 6: Material Handling (Transformer)
Source

Material Handling: HVDC_Material Handling Workshop_(20241119_1).pdf (Pages 30-42)
Integration Note: Aligns with bulk lifting plans and rigging gear.

Executive Summary
Transformer schedules detail ETD/ETA/port/on-site dates. On-shore: Unload → Storage → Inland (DOT permit). Off-shore: SPMT loading → LCT roll-on → Sea fastening. Preparations: PTWs, risk assessments, stability/mooring plans. Receiving: Survey, compaction, jackdown. Preservation: Impact recorder, gas top-up. On-foundation: Skidding. Integration adds bulk lifting/rigging details.
Visual — Core Classes/Relations (Summary)

































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:TransformerunitNo, ETD/ETAtransportedBy → Means (SPMT/LCT)SchedulesDelivery, Installationhvdc:Proceduretype (Top-Up/On-Foundation)requires → Equipment/Document, uses → RiggingGearProcesses, Lifting PlanSafety, Executionhvdc:PreservationCheckgaugeLevel, gasTypeperformsOn → TransformerChecksMaintenance
How it Works (Flow)

Schedules: Origin, ports.
On-Shore: Unload crane → SPMT → Storage → Inland.
Off-Shore: Lift to SPMT → Roll-on → Sea fastening.
Preparations: PTWs, calcs; rigging plans (slingAngle, loadShare).
Receiving: Site survey, jackdown.
Preservation: Recorder test, gauge checks, top-up.
On-Foundation: SPMT/skidding/jacking sequence.


Section 7: Bulk Cargo Operations
Source

Bulk Cargo: 1_CORE-05-hvdc-bulk-cargo-ops.md
Integration Note: Extends material handling with detailed bulk processes.

Executive Summary
Models bulk/project cargo (steel structures, OOG, precast) sea transport, including planning, loading/discharging, stowage/lashing, stability, lifting. Units: m (length), t (weight), deg (angle); coordinates: ship deck local. Boundaries: Data representation/validation; engineering judgments by specialists. Integrated with workshop flows for offshore/marine phases.
Visual — Core Classes/Relations (Summary)





























































ClassKey PropertiesRelationsBasis/Join SourceOutcomehvdc:CargocargoId, type, weight(t), dimsL/W/H(m), cogX/Y/Z(m)placedOn → DeckArea, securedBy → LashingAssembly, handledBy → EquipmentOCR/Table ParserStatus, Integrityhvdc:VesselvesselName, imo?, deckStrength(t/m²)hasDeck → DeckArea, carries → CargoVessel RegistryOperational Statushvdc:DeckAreaareaId, usableL/W/H, maxPointLoadpartOf → Vessel, hosts → CargoDeck LayoutLoad Capacityhvdc:LashingAssemblyrequiredCapacity(t), calcTension(t), safetyFactorappliedTo → Cargo, uses → LashingElementLashing CalcSecuring Strengthhvdc:StabilityCasedisp(t), vcg(m), gm(m), rollAngle(deg)evaluates → Vessel, considers → CargoStability CalcStability Statushvdc:LiftingPlanliftId, method, slingAngleDegfor → Cargo, uses → RiggingGearRigging DesignLifting Planhvdc:Environmentwind(m/s), seaState, tempaffects → LashingAssembly/StabilityCaseWeather APIEnvironmental Impact
How it Works (Flow)

Planning: Data collection/constraints → Draft/Reviewed/Approved plans.
Pre-Operation: Resource allocation/briefing → Mobilized (JSA).
Execution: Loading/lashing/inspection → Completed (QC, photos, surveys).
Post-Operation: Docs/handover → Archived (B/L, COA, reports).


Integrated Ontology System
Domain Ontology
Core Classes (Unified hvdc: Namespace)
turtle@prefix hvdc: <https://hvdc-project.com/ontology/integrated/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# From Material Handling
hvdc:Project a owl:Class .
hvdc:Phase a owl:Class .
hvdc:Port a owl:Class .
hvdc:MOSB a owl:Class .
hvdc:Site a owl:Class .
hvdc:TransportMeans a owl:Class .
hvdc:Operation a owl:Class .
hvdc:Document a owl:Class .

# From Bulk Cargo (Aligned)
hvdc:Cargo a owl:Class .  # Unified with material Cargo
hvdc:Vessel a owl:Class ; rdfs:subClassOf hvdc:TransportMeans .
hvdc:DeckArea a owl:Class .
hvdc:LashingAssembly a owl:Class .
hvdc:LashingElement a owl:Class .
hvdc:StabilityCase a owl:Class .
hvdc:LiftingPlan a owl:Class .
hvdc:RiggingGear a owl:Class .
hvdc:Equipment a owl:Class .
hvdc:Manpower a owl:Class .
hvdc:OperationTask a owl:Class ; rdfs:subClassOf hvdc:Operation .
hvdc:Environment a owl:Class .
Core Properties
turtle# Material Handling Properties
hvdc:hasPhase a owl:ObjectProperty .
hvdc:involves a owl:ObjectProperty .
hvdc:handles a owl:ObjectProperty .
hvdc:consolidates a owl:ObjectProperty .
hvdc:dispatches a owl:ObjectProperty .
hvdc:receives a owl:ObjectProperty .
hvdc:transportedBy a owl:ObjectProperty .
hvdc:usedIn a owl:ObjectProperty .
hvdc:requires a owl:ObjectProperty .
hvdc:projectName a owl:DatatypeProperty .
hvdc:date a owl:DatatypeProperty .
hvdc:phaseType a owl:DatatypeProperty .
hvdc:name a owl:DatatypeProperty .
hvdc:type a owl:DatatypeProperty .
hvdc:areaSqm a owl:DatatypeProperty .
hvdc:weight a owl:DatatypeProperty .
hvdc:dims a owl:DatatypeProperty .
hvdc:voyageTime a owl:DatatypeProperty .

# Bulk Cargo Properties (Integrated)
hvdc:placedOn a owl:ObjectProperty ; rdfs:domain hvdc:Cargo ; rdfs:range hvdc:DeckArea .
hvdc:securedBy a owl:ObjectProperty ; rdfs:domain hvdc:Cargo ; rdfs:range hvdc:LashingAssembly .
hvdc:handledBy a owl:ObjectProperty ; rdfs:domain hvdc:Cargo ; rdfs:range hvdc:Equipment .
hvdc:hasDeck a owl:ObjectProperty ; rdfs:domain hvdc:Vessel ; rdfs:range hvdc:DeckArea .
hvdc:carries a owl:ObjectProperty ; rdfs:domain hvdc:Vessel ; rdfs:range hvdc:Cargo .
hvdc:appliedTo a owl:ObjectProperty ; rdfs:domain hvdc:LashingAssembly ; rdfs:range hvdc:Cargo .
hvdc:uses a owl:ObjectProperty ; rdfs:domain [ owl:unionOf (hvdc:LashingAssembly hvdc:LiftingPlan) ] ; rdfs:range [ owl:unionOf (hvdc:LashingElement hvdc:RiggingGear) ] .
hvdc:evaluates a owl:ObjectProperty ; rdfs:domain hvdc:StabilityCase ; rdfs:range hvdc:Vessel .
hvdc:considers a owl:ObjectProperty ; rdfs:domain hvdc:StabilityCase ; rdfs:range hvdc:Cargo .
hvdc:for a owl:ObjectProperty ; rdfs:domain hvdc:LiftingPlan ; rdfs:range hvdc:Cargo .
hvdc:affects a owl:ObjectProperty ; rdfs:domain hvdc:Environment ; rdfs:range [ owl:unionOf (hvdc:LashingAssembly hvdc:StabilityCase) ] .
hvdc:cargoId a owl:DatatypeProperty .
hvdc:stackable a owl:DatatypeProperty ; rdfs:range xsd:boolean .
hvdc:deckStrength a owl:DatatypeProperty .
hvdc:requiredCapacity a owl:DatatypeProperty .
hvdc:safetyFactor a owl:DatatypeProperty .
hvdc:disp a owl:DatatypeProperty .
hvdc:vcg a owl:DatatypeProperty .
hvdc:gm a owl:DatatypeProperty .
hvdc:rollAngle a owl:DatatypeProperty .
hvdc:slingAngleDeg a owl:DatatypeProperty .
hvdc:wind a owl:DatatypeProperty .
hvdc:seaState a owl:DatatypeProperty .
SHACL Constraints
turtle# Material Handling Constraints (Excerpt)
hvdc:ProjectShape a sh:NodeShape ;
    sh:targetClass hvdc:Project ;
    sh:property [ sh:path hvdc:projectName ; sh:minCount 1 ] .

# Bulk Cargo Constraints (Integrated)
hvdc:CargoShape a sh:NodeShape ;
    sh:targetClass hvdc:Cargo ;
    sh:property [ sh:path hvdc:weight ; sh:minInclusive 0.01 ] ;
    sh:property [ sh:path hvdc:dimsL ; sh:minInclusive 0.01 ] .  # Assuming dims split into L/W/H

hvdc:VesselShape a sh:NodeShape ;
    sh:targetClass hvdc:Vessel ;
    sh:property [ sh:path hvdc:deckStrength ; sh:minInclusive 0.01 ] .

hvdc:LashingAssemblyShape a sh:NodeShape ;
    sh:targetClass hvdc:LashingAssembly ;
    sh:property [ sh:path hvdc:safetyFactor ; sh:minInclusive 1.0 ] .

hvdc:StabilityCaseShape a sh:NodeShape ;
    sh:targetClass hvdc:StabilityCase ;
    sh:property [ sh:path hvdc:gm ; sh:minInclusive 0.0 ] ;
    sh:property [ sh:path hvdc:rollAngle ; sh:maxInclusive 90.0 ] .
JSON-LD Examples
Integrated Cargo Example
json{
  "@context": {
    "hvdc": "https://hvdc-project.com/ontology/integrated/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  },
  "@id": "hvdc:cargo-001",
  "@type": "hvdc:Cargo",
  "hvdc:cargoId": "CGO-2025-001",
  "hvdc:type": "Steel Structure",
  "hvdc:weight": 25.5,
  "hvdc:dims": "L:12.0 W:3.5 H:4.2",
  "hvdc:cogX": 6.0,
  "hvdc:stackable": false,
  "hvdc:placedOn": {
    "@type": "hvdc:DeckArea",
    "hvdc:areaId": "DECK-A1",
    "hvdc:maxPointLoad": 50.0
  },
  "hvdc:securedBy": {
    "@type": "hvdc:LashingAssembly",
    "hvdc:safetyFactor": 1.2
  },
  "hvdc:transportedBy": {
    "@type": "hvdc:TransportMeans",
    "hvdc:type": "LCT"
  }
}
Transformer with Bulk Lifting
json{
  "@context": {
    "hvdc": "https://hvdc-project.com/ontology/integrated/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  },
  "@id": "hvdc:transformer-001",
  "@type": "hvdc:Cargo",
  "hvdc:type": "Transformer",
  "hvdc:weight": 200.0,
  "hvdc:dims": "L:10m W:5m H:6m",
  "hvdc:for": {
    "@type": "hvdc:LiftingPlan",
    "hvdc:method": "Skidding",
    "hvdc:slingAngleDeg": 45,
    "hvdc:uses": {
      "@type": "hvdc:RiggingGear",
      "hvdc:type": "Sling"
    }
  }
}
SPARQL Queries
Cargo Stability Query
sparqlPREFIX hvdc: <https://hvdc-project.com/ontology/integrated/>

SELECT ?cargoId ?weight ?gm ?stabilityStatus
WHERE {
    ?cargo hvdc:cargoId ?cargoId ;
           hvdc:weight ?weight .
    ?stability hvdc:considers ?cargo ;
               hvdc:gm ?gm .
    BIND (IF(?gm > 0.5, "STABLE", IF(?gm > 0.2, "MARGINAL", "UNSTABLE")) AS ?stabilityStatus)
}
ORDER BY DESC(?gm)
Operation Documents Query
sparqlPREFIX hvdc: <https://hvdc-project.com/ontology/integrated/>

SELECT ?operationType ?documentType
WHERE {
    ?operation hvdc:type ?operationType ;
               hvdc:requires ?document .
    ?document hvdc:type ?documentType .
}
ORDER BY ?operationType
Semantic KPI Layer
Integrated KPIs

Cargo Safety Index: Stability compliance rate across phases.
Lashing Efficiency: Capacity vs. usage in marine transport.
Deck Utilization: Area exploitation in MOSB/vessels.
Handling Incident Rate: Zero targets in lifting/stowage.
Preservation Adherence: Temp/RH compliance for bulk items.
Voyage Optimization: Actual vs. planned times with stability factors.
