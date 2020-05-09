import { PanelLayout, Widget } from "@lumino/widgets";

import { FileBrowser } from "@jupyterlab/filebrowser";

import { S3Drive } from "./contents";

import { IDocumentManager } from "@jupyterlab/docmanager";

/**
 * Widget for hosting the S3 filebrowser.
 */
export class S3FileBrowser extends Widget {
  constructor(browser: FileBrowser, drive: S3Drive, manager: IDocumentManager) {
    super();
    this.addClass("jp-S3Browser");
    this.layout = new PanelLayout();
    (this.layout as PanelLayout).addWidget(browser);
    browser.model.refresh();
  }
}
