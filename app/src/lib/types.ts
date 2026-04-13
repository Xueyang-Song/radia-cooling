export interface StoryStat {
  label: string
  value: string
  detail: string
}

export interface StoryCard {
  id: string
  title: string
  summary: string
  detail: string
}

export interface ProjectInfo {
  title: string
  subtitle: string
  summary: string
  finalVerdict: string
  heroStats: StoryStat[]
  cards: StoryCard[]
}

export interface DesignSpace {
  functionalLayers: number
  materials: string[]
  reflectorMaterial: string
  reflectorThicknessNm: number
  thicknessMinNm: number
  thicknessMaxNm: number
  wavelengthStartUm: number
  wavelengthStopUm: number
  wavelengthPoints: number
  solarBand: [number, number]
  windowBand: [number, number]
}

export interface RangeSummary {
  min: number
  max: number
}

export interface DatasetSample {
  id: string
  label: string
  note: string
  sampleId: string
  targets: Record<string, number>
  layerMaterials: string[]
  layerThicknessesNm: number[]
  totalThicknessNm: number
  reflectance: number[]
  emissivity: number[]
}

export interface DatasetSummary {
  backend: string
  numSamples: number
  seed: number
  stats: {
    solarReflectance: RangeSummary
    windowEmissivity: RangeSummary
    coolingPowerProxy: RangeSummary
    totalThicknessNm: RangeSummary
  }
  wavelengths: number[]
  selectedSamples: DatasetSample[]
}

export interface PipelineStep {
  id: string
  title: string
  why: string
  inputs: string[]
  outputs: string[]
  sourcePaths: string[]
  evidenceFiles: EvidenceFile[]
}

export interface EvidenceFile {
  id: string
  title: string
  language: string
  sourcePath: string
  content: string
}

export interface CandidateShowcaseItem {
  id: string
  label: string
  family: string
  route: string
  note: string
  sourcePath: string
  sampleId: string
  targets: Record<string, number>
  simulated: Record<string, number>
  absoluteError: Record<string, number>
  totalAbsoluteError: number
  layerMaterials: string[]
  layerThicknessesNm: number[]
  reflectorMaterial: string
  reflectorThicknessNm: number
}

export interface ModelSummary {
  id: string
  name: string
  family: string
  status: 'baseline' | 'retained' | 'competitive' | 'rejected'
  summary: string
  splitMode: string
  device: string
  metrics: Record<string, number>
  verifiedHighlights: Record<string, number>
}

export interface TargetContender {
  label: string
  value: number
  status: 'baseline' | 'retained' | 'competitive' | 'rejected'
  sourcePath: string
}

export interface TargetResult {
  id: string
  label: string
  summary: string
  targetMetrics: Record<string, number>
  contenders: TargetContender[]
}

export interface ComparisonSummary {
  retainedWorkflow: {
    title: string
    summary: string
    steps: string[]
  }
  models: ModelSummary[]
  targetResults: TargetResult[]
  candidateShowcase: CandidateShowcaseItem[]
}

export interface TimelineEvent {
  id: string
  title: string
  summary: string
  evidence: string[]
  evidenceFiles: EvidenceFile[]
}

export interface GlossaryTerm {
  term: string
  explanation: string
}

export interface ResearchLibraryMeta {
  docCount: number
  paperCount: number
  pdfCount: number
  openAccessCount: number
  note: string
}

export interface NotebookMetric {
  label: string
  value: string
  detail: string
  tone: 'cool' | 'warm' | 'neutral'
}

export interface NotebookCommand {
  label: string
  command: string
  note: string
  sourcePaths: string[]
}

export interface NotebookPanel {
  id: string
  kind: 'code' | 'artifact'
  title: string
  language: string
  sourcePath: string
  content: string
}

export interface NotebookStage {
  id: string
  eyebrow: string
  title: string
  summary: string
  meaning: string
  metrics: NotebookMetric[]
  commands: NotebookCommand[]
  panels: NotebookPanel[]
  takeaways: string[]
}

export interface LabNotebook {
  intro: string
  stages: NotebookStage[]
}

export interface FileOfRecord {
  label: string
  path: string
  viewer: EvidenceFile
}

export interface SiteData {
  generatedAt: string
  project: ProjectInfo
  designSpace: DesignSpace
  dataset: DatasetSummary
  pipeline: {
    steps: PipelineStep[]
  }
  comparison: ComparisonSummary
  labNotebook: LabNotebook
  timeline: TimelineEvent[]
  glossary: GlossaryTerm[]
  researchLibrary: ResearchLibraryMeta
  filesOfRecord: FileOfRecord[]
}

export interface ResearchDoc {
  id: string
  title: string
  summary: string
  body: string
  type: 'markdown'
  sourcePath: string
}

export interface ResearchPaper {
  id: string
  title: string
  authors: string
  year: number | null
  venue: string
  category: string
  summary: string
  citationCount: string
  doi: string | null
  officialUrl: string | null
  openAccessPdfUrl: string | null
  downloadedPdfPath: string | null
  pdfSizeBytes: number | null
  status: 'downloaded' | 'open-access-link' | 'citation-only'
  sourcePath: string
}

export interface ResearchPayload {
  documents: ResearchDoc[]
  papers: ResearchPaper[]
}