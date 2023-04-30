import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InferencePageComponent } from './inference-page.component';

describe('InferencePageComponent', () => {
  let component: InferencePageComponent;
  let fixture: ComponentFixture<InferencePageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InferencePageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InferencePageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
