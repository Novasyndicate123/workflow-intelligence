class AcquisitionReviewBatch:
    @staticmethod
    def build(prospects):
        result = []
        for prospect in prospects:
            updated_prospect = prospect.copy()
            updated_prospect['review_status'] = 'READY_FOR_HUMAN_REVIEW'
            updated_prospect['external_send_authorized'] = False
            updated_prospect['execution_authorized'] = False
            result.append(updated_prospect)
        result.sort(
            key=lambda x: (-x.get('qualification_score', 0), x.get('business_name', ''))
        )
        return result
