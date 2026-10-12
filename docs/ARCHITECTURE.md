# System Architecture

## Overview

NovaFlow is a modular analytics system designed for quarterly business metric analysis. The architecture follows a clean, layered approach with separation of concerns.

## Components

### 1. Data Layer (`DataValidator`)
- CSV file loading
- Schema validation
- Data type checking
- Error reporting

### 2. Analysis Layer (`DataAnalyzer`)
- Metric loading and transformation
- Summary statistics calculation
- Trend detection
- Critical metric identification

### 3. Report Layer (`ReportGenerator`)
- SVG chart generation
- HTML dashboard rendering
- JSON export
- Multi-format output

### 4. Application Layer (`App`)
- Workflow orchestration
- Report generation
- Dashboard serving
- Error handling

## Data Flow

```
CSV File
   ↓
DataValidator (validate)
   ↓
DataAnalyzer (analyze)
   ↓
ReportGenerator (render)
   ↓
Output (JSON/HTML)
```

## Module Structure

```
src/
├── main.py              # Core analytics engine
├── cli.py               # Command-line interface
└── __init__.py
```

## Design Principles

1. **No External Dependencies** - Pure Python standard library only
2. **Modularity** - Each component has a single responsibility
3. **Testability** - Clean interfaces for unit testing
4. **Scalability** - Easy to extend with new analysis features
5. **Error Handling** - Comprehensive validation and reporting
