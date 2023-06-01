export class InferenceResponse {
    name: string;
    description: string;
    isDisease: boolean;
    products: Record<string, string>[];
    treatments: Record<string, string>[];

    constructor(Name: string, Description: string, isDisease: boolean, Treatments:Record<string, string>[], Products: Record<string, string>[]) {
      this.name = Name;
      this.description = Description;
      this.isDisease = isDisease;
      this.products = Treatments;
      this.treatments = Products;
    }
}
