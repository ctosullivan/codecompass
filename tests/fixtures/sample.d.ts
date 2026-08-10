export interface Options {
  headingStyle?: "setext" | "atx";
}

export default class TurndownService {
  constructor(options?: Options);
  turndown(html: string): string;
}
