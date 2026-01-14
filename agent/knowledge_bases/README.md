# Knowledge Bases Directory

This directory contains PDF documents used for RAG (Retrieval-Augmented Generation).

## Contents

- **Pet Store Product Catalog.pdf** (129 KB) - Product listings and specifications
- **Pet Store Product Content.pdf** (108 KB) - Product descriptions and details

## Purpose

These PDFs are used by the agent for product information retrieval:

1. **LlamaIndex Local RAG** (Current Implementation)
   - PDFs are also stored in `agent/pet_store_agent/data/`
   - LlamaIndex builds a local vector store from these documents
   - Stored in `agent/pet_store_agent/storage/`
   - No AWS Knowledge Bases required

2. **AWS Knowledge Bases** (Alternative)
   - These PDFs can be uploaded to AWS Knowledge Bases
   - Provides cloud-based RAG solution
   - Not currently used but available as an option

## Current Usage

The agent currently uses **LlamaIndex** with local PDFs from the `data/` directory. The same PDFs are kept here for potential AWS Knowledge Bases integration.

## Notes

- PDFs in this directory and `agent/pet_store_agent/data/` should be kept in sync
- LlamaIndex builds embeddings on first run
- Vector store persists in `agent/pet_store_agent/storage/`
